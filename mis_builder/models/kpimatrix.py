# Copyright 2014 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import logging
from collections import OrderedDict, defaultdict

from odoo.exceptions import UserError

from .accounting_none import AccountingNone
from .mis_kpi_data import ACC_SUM
from .mis_safe_eval import DataError, mis_safe_eval
from .simple_array import SimpleArray

_logger = logging.getLogger(__name__)


class KpiMatrixRow:
    # Detail rows are keyed by (detail_model, detail_id). Currently supported
    # detail models are account.account and res.partner.

    def __init__(self, matrix, kpi, detail_id=None, parent_row=None, detail_model=None):
        self._matrix = matrix
        self.kpi = kpi
        self.detail_id = detail_id
        self.detail_model = detail_model
        self.description = ""
        self.parent_row = parent_row
        if self.detail_id is None:
            self.style_props = self._matrix._style_model.merge(
                [self.kpi.report_id.style_id, self.kpi.style_id]
            )
        else:
            self.style_props = self._matrix._style_model.merge(
                [self.kpi.report_id.style_id, self.kpi.auto_expand_accounts_style_id]
            )

    @property
    def account_id(self):
        """Backward-compatible alias for account detail rows."""
        if self.detail_model == self._matrix.account_model_name:
            return self.detail_id
        return None

    @property
    def label(self):
        if self.detail_id is None:
            return self.kpi.description
        return self._matrix.get_detail_name(self.detail_model, self.detail_id)

    def iter_cell_tuples(self, cols=None):
        if cols is None:
            cols = self._matrix.iter_cols()
        for col in cols:
            yield col.get_cell_tuple_for_row(self)

    def iter_cells(self, subcols=None):
        if subcols is None:
            subcols = self._matrix.iter_subcols()
        for subcol in subcols:
            yield subcol.get_cell_for_row(self)

    def is_empty(self):
        for cell in self.iter_cells():
            if cell and cell.val not in (AccountingNone, None):
                return False
        return True


class KpiMatrixCol:
    def __init__(self, key, label, description, locals_dict, subkpis):
        self.key = key
        self.label = label
        self.description = description
        self.locals_dict = locals_dict
        self.colspan = subkpis and len(subkpis) or 1
        self._subcols = []
        self.subkpis = subkpis
        if not subkpis:
            subcol = KpiMatrixSubCol(self, "", "", 0)
            self._subcols.append(subcol)
        else:
            for i, subkpi in enumerate(subkpis):
                subcol = KpiMatrixSubCol(self, subkpi.description, "", i)
                self._subcols.append(subcol)
        self._cell_tuples_by_row = {}  # {row: (cells tuple)}

    def _set_cell_tuple(self, row, cell_tuple):
        self._cell_tuples_by_row[row] = cell_tuple

    def iter_subcols(self):
        return self._subcols

    def iter_cell_tuples(self):
        return self._cell_tuples_by_row.values()

    def get_cell_tuple_for_row(self, row):
        return self._cell_tuples_by_row.get(row)


class KpiMatrixSubCol:
    def __init__(self, col, label, description, index=0):
        self.col = col
        self.label = label
        self.description = description
        self.index = index

    @property
    def subkpi(self):
        if self.col.subkpis:
            return self.col.subkpis[self.index]

    def iter_cells(self):
        for cell_tuple in self.col.iter_cell_tuples():
            yield cell_tuple[self.index]

    def get_cell_for_row(self, row):
        cell_tuple = self.col.get_cell_tuple_for_row(row)
        if cell_tuple is None:
            return None
        return cell_tuple[self.index]


class KpiMatrixCell:  # noqa: B903 (immutable data class)
    def __init__(
        self,
        row,
        subcol,
        val,
        val_rendered,
        val_comment,
        style_props,
        drilldown_arg,
        val_type,
    ):
        self.row = row
        self.subcol = subcol
        self.val = val
        self.val_rendered = val_rendered
        self.val_comment = val_comment
        self.style_props = style_props
        self.drilldown_arg = drilldown_arg
        self.val_type = val_type
        self.cell_id = KpiMatrix._pack_cell_id(self)


class KpiMatrix:
    def __init__(
        self,
        env,
        companies=None,
        account_model="account.account",
    ):
        # cache language id for faster rendering
        lang_model = env["res.lang"]
        self.lang = lang_model._lang_get(env.user.lang)
        self._style_model = env["mis.report.style"]
        self.account_model_name = account_model
        self._account_model = env[account_model]
        self._partner_model = env["res.partner"]
        self._companies = companies
        # data structures
        # { kpi: KpiMatrixRow }
        self._kpi_rows = OrderedDict()
        # { kpi: {(detail_model, detail_id): KpiMatrixRow} }
        self._detail_rows = {}
        # { col_key: KpiMatrixCol }
        self._cols = OrderedDict()
        # { col_key (left of comparison): [(col_key, base_col_key)] }
        self._comparison_todo = defaultdict(list)
        # { col_key (left of sum): (col_key, [(sign, sum_col_key)])
        self._sum_todo = {}
        # { (detail_model, detail_id): display name }
        self._detail_names = {}

    def declare_kpi(self, kpi):
        """Declare a new kpi (row) in the matrix.

        Invoke this first for all kpi, in display order.
        """
        self._kpi_rows[kpi] = KpiMatrixRow(self, kpi)
        self._detail_rows[kpi] = {}

    def declare_col(self, col_key, label, description, locals_dict, subkpis):
        """Declare a new column, giving it an identifier (key).

        Invoke the declare_* methods in display order.
        """
        col = KpiMatrixCol(col_key, label, description, locals_dict, subkpis)
        self._cols[col_key] = col
        return col

    def declare_comparison(
        self, cmpcol_key, col_key, base_col_key, label, description=None
    ):
        """Declare a new comparison column.

        Invoke the declare_* methods in display order.
        """
        self._comparison_todo[cmpcol_key] = (col_key, base_col_key, label, description)
        self._cols[cmpcol_key] = None  # reserve slot in insertion order

    def declare_sum(
        self, sumcol_key, col_to_sum_keys, label, description=None, sum_accdet=False
    ):
        """Declare a new summation column.

        Invoke the declare_* methods in display order.
        :param col_to_sum_keys: [(sign, col_key)]
        """
        self._sum_todo[sumcol_key] = (col_to_sum_keys, label, description, sum_accdet)
        self._cols[sumcol_key] = None  # reserve slot in insertion order

    def set_values(self, kpi, col_key, vals, drilldown_args, tooltips=True):
        """Set values for a kpi and a colum.

        Invoke this after declaring the kpi and the column.
        """
        self.set_values_detail(
            kpi, col_key, None, vals, drilldown_args, tooltips=tooltips
        )

    def set_values_detail_account(
        self, kpi, col_key, account_id, vals, drilldown_args, tooltips=True
    ):
        """Backward-compatible wrapper around set_values_detail."""
        return self.set_values_detail(
            kpi,
            col_key,
            account_id,
            vals,
            drilldown_args,
            tooltips=tooltips,
            detail_model=self.account_model_name if account_id is not None else None,
        )

    def set_values_detail(
        self,
        kpi,
        col_key,
        detail_id,
        vals,
        drilldown_args,
        tooltips=True,
        detail_model=None,
    ):
        """Set values for a kpi, column and optional detail row."""
        if detail_id is None:
            row = self._kpi_rows[kpi]
        else:
            if detail_model is None:
                detail_model = self.account_model_name
            kpi_row = self._kpi_rows[kpi]
            detail_key = (detail_model, detail_id)
            if detail_key in self._detail_rows[kpi]:
                row = self._detail_rows[kpi][detail_key]
            else:
                row = KpiMatrixRow(
                    self,
                    kpi,
                    detail_id,
                    parent_row=kpi_row,
                    detail_model=detail_model,
                )
                self._detail_rows[kpi][detail_key] = row
        col = self._cols[col_key]
        cell_tuple = []
        assert len(vals) == col.colspan
        assert len(drilldown_args) == col.colspan
        style_name = None
        for val, drilldown_arg, subcol in zip(
            vals, drilldown_args, col.iter_subcols(), strict=True
        ):
            if isinstance(val, DataError):
                val_rendered = val.name
                val_comment = val.msg
            else:
                val_rendered = self._style_model.render(
                    self.lang, row.style_props, kpi.type, val
                )
                if row.kpi.multi and subcol.subkpi:
                    val_comment = (
                        f"{row.kpi.name}.{subcol.subkpi.name} = "
                        f"{row.kpi._get_expression_str_for_subkpi(subcol.subkpi)}"
                    )
                else:
                    val_comment = f"{row.kpi.name} = {row.kpi.expression}"
            cell_style_props = row.style_props
            if row.kpi.style_expression:
                # evaluate style expression
                try:
                    style_name = mis_safe_eval(
                        row.kpi.style_expression, col.locals_dict
                    )
                except Exception:
                    _logger.error(
                        "Error evaluating style expression <%s>",
                        row.kpi.style_expression,
                        exc_info=True,
                    )
                    style_name = None
                if style_name:
                    style = self._style_model.search([("name", "=", style_name)])
                    if style:
                        cell_style_props = self._style_model.merge(
                            [row.style_props, style[0]]
                        )
                    else:
                        _logger.error("Style '%s' not found.", style_name)
            cell = KpiMatrixCell(
                row,
                subcol,
                val,
                val_rendered,
                tooltips and val_comment or None,
                cell_style_props,
                drilldown_arg,
                kpi.type,
            )
            cell_tuple.append(cell)
        assert len(cell_tuple) == col.colspan
        col._set_cell_tuple(row, cell_tuple)

    def _common_subkpis(self, cols):
        if not cols:
            return set()
        common_subkpis = set(cols[0].subkpis)
        for col in cols[1:]:
            common_subkpis = common_subkpis & set(col.subkpis)
        return common_subkpis

    def compute_comparisons(self):
        """Compute comparisons.

        Invoke this after setting all values.
        """
        for (
            cmpcol_key,
            (col_key, base_col_key, label, description),
        ) in self._comparison_todo.items():
            col = self._cols[col_key]
            base_col = self._cols[base_col_key]
            common_subkpis = self._common_subkpis([col, base_col])
            if (col.subkpis or base_col.subkpis) and not common_subkpis:
                raise UserError(
                    self.env._(
                        "Columns %(descr)s and %(base_descr)s are not comparable",
                        descr=col.description,
                        base_descr=base_col.description,
                    )
                )
            if not label:
                label = f"{col.label} vs {base_col.label}"
            comparison_col = KpiMatrixCol(
                cmpcol_key,
                label,
                description,
                {},
                sorted(common_subkpis, key=lambda s: s.sequence),
            )
            self._cols[cmpcol_key] = comparison_col
            for row in self.iter_rows():
                cell_tuple = col.get_cell_tuple_for_row(row)
                base_cell_tuple = base_col.get_cell_tuple_for_row(row)
                if cell_tuple is None and base_cell_tuple is None:
                    continue
                if cell_tuple is None:
                    vals = [AccountingNone] * (len(common_subkpis) or 1)
                else:
                    vals = [
                        cell.val
                        for cell in cell_tuple
                        if not common_subkpis or cell.subcol.subkpi in common_subkpis
                    ]
                if base_cell_tuple is None:
                    base_vals = [AccountingNone] * (len(common_subkpis) or 1)
                else:
                    base_vals = [
                        cell.val
                        for cell in base_cell_tuple
                        if not common_subkpis or cell.subcol.subkpi in common_subkpis
                    ]
                comparison_cell_tuple = []
                for val, base_val, comparison_subcol in zip(
                    vals,
                    base_vals,
                    comparison_col.iter_subcols(),
                    strict=True,
                ):
                    # TODO FIXME average factors
                    comparison = self._style_model.compare_and_render(
                        self.lang,
                        row.style_props,
                        row.kpi.type,
                        row.kpi.compare_method,
                        val,
                        base_val,
                        1,
                        1,
                    )
                    delta, delta_r, delta_style, delta_type = comparison
                    comparison_cell_tuple.append(
                        KpiMatrixCell(
                            row,
                            comparison_subcol,
                            delta,
                            delta_r,
                            None,
                            delta_style,
                            None,
                            delta_type,
                        )
                    )
                comparison_col._set_cell_tuple(row, comparison_cell_tuple)

    def compute_sums(self):
        """Compute comparisons.

        Invoke this after setting all values.
        """
        for (
            sumcol_key,
            (col_to_sum_keys, label, description, sum_accdet),
        ) in self._sum_todo.items():
            sumcols = [self._cols[k] for (sign, k) in col_to_sum_keys]
            # TODO check all sumcols are resolved; we need a kind of
            #      recompute queue here so we don't depend on insertion
            #      order
            common_subkpis = self._common_subkpis(sumcols)
            if any(c.subkpis for c in sumcols) and not common_subkpis:
                raise UserError(
                    self.env._(
                        "Sum cannot be computed in column %s "
                        "because the columns to sum have no "
                        "common subkpis",
                        label,
                    )
                )
            sum_col = KpiMatrixCol(
                sumcol_key,
                label,
                description,
                {},
                sorted(common_subkpis, key=lambda s: s.sequence),
            )
            self._cols[sumcol_key] = sum_col
            for row in self.iter_rows():
                acc = SimpleArray([AccountingNone] * (len(common_subkpis) or 1))
                if row.kpi.accumulation_method == ACC_SUM and not (
                    row.detail_id is not None and not sum_accdet
                ):
                    for sign, col_to_sum in col_to_sum_keys:
                        cell_tuple = self._cols[col_to_sum].get_cell_tuple_for_row(row)
                        if cell_tuple is None:
                            vals = [AccountingNone] * (len(common_subkpis) or 1)
                        else:
                            vals = [
                                cell.val
                                for cell in cell_tuple
                                if not common_subkpis
                                or cell.subcol.subkpi in common_subkpis
                            ]
                        if sign == "+":
                            acc += SimpleArray(vals)
                        else:
                            acc -= SimpleArray(vals)
                self.set_values_detail(
                    row.kpi,
                    sumcol_key,
                    row.detail_id,
                    acc,
                    [None] * (len(common_subkpis) or 1),
                    tooltips=False,
                    detail_model=row.detail_model,
                )

    def iter_rows(self):
        """Iterate rows in display order.

        yields KpiMatrixRow.
        """
        for kpi_row in self._kpi_rows.values():
            yield kpi_row
            detail_rows = self._detail_rows[kpi_row.kpi].values()
            detail_rows = sorted(detail_rows, key=lambda r: r.label)
            yield from detail_rows

    def iter_cols(self):
        """Iterate columns in display order.

        yields KpiMatrixCol: one for each column or comparison.
        """
        for _col_key, col in self._cols.items():
            yield col

    def iter_subcols(self):
        """Iterate sub columns in display order.

        yields KpiMatrixSubCol: one for each subkpi in each column
        and comparison.
        """
        for col in self.iter_cols():
            yield from col.iter_subcols()

    def _load_detail_names(self):
        account_ids = set()
        partner_ids = set()
        for detail_rows in self._detail_rows.values():
            for detail_model, detail_id in detail_rows:
                if detail_model == self.account_model_name:
                    account_ids.add(detail_id)
                elif detail_model == "res.partner":
                    partner_ids.add(detail_id)
        if account_ids:
            accounts = self._account_model.search([("id", "in", list(account_ids))])
            for account in accounts:
                self._detail_names[(self.account_model_name, account.id)] = (
                    self._get_account_name(account)
                )
        if partner_ids:
            # 0 is the sentinel used for move lines without partner
            resolved_ids = [i for i in partner_ids if i]
            partners = self._partner_model.browse(resolved_ids)
            for partner in partners:
                self._detail_names[("res.partner", partner.id)] = partner.display_name
            if 0 in partner_ids:
                self._detail_names[("res.partner", 0)] = self._partner_model.env._(
                    "(No partner)"
                )

    def _get_account_name(self, account):
        # display_name is account code + account name. Note the account may have
        # no code for the user current active company, in which case only the
        # name is displayed. It is consistent with other places where accounts
        # are displayed in Odoo.
        account_companies = (
            account.company_ids & self._companies
            if self._companies
            else account.company_ids
        )
        if len(account_companies) == 1:
            # When there is no ambiguity on the company, use it to compute the label
            account_name = account.with_company(account_companies).display_name
        else:
            # Otherwise use the default Odoo behaviour to get the account label
            # (this may return a name without code)
            account_name = account.display_name
        is_multi_company = self._companies and len(self._companies) > 1
        if is_multi_company and len(account_companies) == 1:
            # In a multi-company report, if the account is bound to one
            # company, it makes sense to show the company name. If the account
            # is bound to multiple companies it does not make sense, because we
            # don't know to which companies this detail line effectively
            # contributes, so the list of companies in it would not add useful
            # information.
            account_name = f"{account_name} [{account_companies.display_name}]"
        return account_name

    def get_detail_name(self, detail_model, detail_id):
        key = (detail_model, detail_id)
        if key not in self._detail_names:
            self._load_detail_names()
        return self._detail_names.get(key, "")

    def get_account_name(self, account_id):
        return self.get_detail_name(self.account_model_name, account_id)

    def as_dict(self):
        header = [{"cols": []}, {"cols": []}]
        for col in self.iter_cols():
            header[0]["cols"].append(
                {
                    "label": col.label,
                    "description": col.description,
                    "colspan": col.colspan,
                }
            )
            for subcol in col.iter_subcols():
                header[1]["cols"].append(
                    {
                        "label": subcol.label,
                        "description": subcol.description,
                        "colspan": 1,
                    }
                )

        body = []
        for row in self.iter_rows():
            if (
                row.style_props.hide_empty and row.is_empty()
            ) or row.style_props.hide_always:
                continue
            row_data = {
                "label": row.label,
                "description": row.description,
                "style": self._style_model.to_css_style(row.style_props),
                "cells": [],
            }
            for cell in row.iter_cells():
                if cell is None:
                    # TODO use subcol style here
                    row_data["cells"].append({})
                else:
                    if cell.val is AccountingNone or isinstance(cell.val, DataError):
                        val = None
                    else:
                        val = cell.val
                    col_data = {
                        "cell_id": cell.cell_id,
                        "val": val,
                        "val_r": cell.val_rendered,
                        "val_c": cell.val_comment,
                        "style": self._style_model.to_css_style(
                            cell.style_props, no_indent=True
                        ),
                        # notes can not be added on detail lines
                        "can_be_annotated": cell.row.detail_id is None,
                    }
                    if cell.drilldown_arg:
                        col_data["drilldown_arg"] = cell.drilldown_arg
                    row_data["cells"].append(col_data)
            body.append(row_data)

        return {"header": header, "body": body}

    # Logic to convert semantic coordinates (period, kpi, subkpi)
    # to visual coordinates (cell id) and back. The rendering logic musn't know
    # about semantic concepts such as periods and kpis. Having these well identified
    # methods allow us to easily spot where the conversion between the rendering and
    # semantic domain occur.

    @classmethod
    def _detail_key_to_cell_token(cls, detail_model, detail_id):
        if detail_id is None:
            return ""
        if detail_model == "res.partner":
            return f"p:{detail_id}"
        # account details keep the historic numeric token for compatibility
        return str(detail_id)

    @classmethod
    def _make_cell_id(
        cls,
        kpi_id: int,
        detail_id: int | None,
        period_id: int,
        subkpi_id: int | None,
        detail_model: str | None = None,
    ) -> str:
        mid = cls._detail_key_to_cell_token(detail_model, detail_id)
        return f"{kpi_id}#{mid}#{period_id}#{subkpi_id or ''}"

    @classmethod
    def _pack_cell_id(cls, cell: KpiMatrixCell) -> str:
        return cls._make_cell_id(
            cell.row.kpi.id,
            cell.row.detail_id,
            cell.subcol.col.key,
            cell.subcol.subkpi and cell.subcol.subkpi.id,
            detail_model=cell.row.detail_model,
        )

    @classmethod
    def _unpack_cell_id(cls, cell_id: str) -> tuple[int, int | None, int, int | None]:
        """Unpack a cell id.

        The second element is the detail id. For partner details the raw token
        is not returned here; callers that need the model should use
        `_unpack_cell_id_detail`.
        """
        kpi_id, detail_id, period_id, subkpi_id = cls._unpack_cell_id_detail(cell_id)[
            :4
        ]
        return kpi_id, detail_id, period_id, subkpi_id

    @classmethod
    def _unpack_cell_id_detail(
        cls, cell_id: str
    ) -> tuple[int, int | None, int, int | None, str | None]:
        kpi_id, mid, col_key, subkpi_id = cell_id.split("#")
        kpi_id = int(kpi_id)
        period_id = int(col_key)
        subkpi_id = int(subkpi_id) if subkpi_id else None
        detail_model = None
        detail_id = None
        if mid.startswith("p:"):
            detail_model = "res.partner"
            detail_id = int(mid[2:])
        elif mid:
            detail_model = "account.account"
            detail_id = int(mid)
        return kpi_id, detail_id, period_id, subkpi_id, detail_model
