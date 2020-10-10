# Copyright 2014 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import datetime
import logging

from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError

from .aep import AccountingExpressionProcessor as AEP
from .expression_evaluator import ExpressionEvaluator

_logger = logging.getLogger(__name__)


SRC_ACTUALS = "actuals"
SRC_ACTUALS_ALT = "actuals_alt"
SRC_CMPCOL = "cmpcol"
SRC_SUMCOL = "sumcol"

MODE_NONE = "none"
MODE_FIX = "fix"
MODE_REL = "relative"


class DateFilterRequired(ValidationError):
    pass


class DateFilterForbidden(ValidationError):
    pass


class MisReportInstancePeriodSum(models.Model):

    _name = "mis.report.instance.period.sum"
    _description = "MIS Report Instance Period Sum"

    period_id = fields.Many2one(
        comodel_name="mis.report.instance.period",
        string="Parent column",
        ondelete="cascade",
        required=True,
    )
    period_to_sum_id = fields.Many2one(
        comodel_name="mis.report.instance.period",
        string="Column",
        ondelete="restrict",
        required=True,
    )
    sign = fields.Selection([("+", "+"), ("-", "-")], required=True, default="+")

    @api.constrains("period_id", "period_to_sum_id")
    def _check_period_to_sum(self):
        for rec in self:
            if rec.period_id == rec.period_to_sum_id:
                raise ValidationError(
                    _("You cannot sum period %s with itself.") % rec.period_id.name
                )


class MisReportInstancePeriod(models.Model):
    """A MIS report instance has the logic to compute
    a report template for a given date period.

    Periods have a duration (day, week, fiscal period) and
    are defined as an offset relative to a pivot date.
    """

    @api.depends(
        "report_instance_id.pivot_date",
        "report_instance_id.comparison_mode",
        "date_range_type_id",
        "type",
        "offset",
        "duration",
        "mode",
        "manual_date_from",
        "manual_date_to",
        "is_ytd",
    )
    def _compute_dates(self):
        for record in self:
            record.date_from = False
            record.date_to = False
            record.valid = False
            report = record.report_instance_id
            d = fields.Date.from_string(report.pivot_date)
            if not report.comparison_mode:
                record.date_from = report.date_from
                record.date_to = report.date_to
                record.valid = record.date_from and record.date_to
            elif record.mode == MODE_NONE:
                record.date_from = False
                record.date_to = False
                record.valid = True
            elif record.mode == MODE_FIX:
                record.date_from = record.manual_date_from
                record.date_to = record.manual_date_to
                record.valid = record.date_from and record.date_to
            elif record.mode == MODE_REL and record.type == "d":
                date_from = d + datetime.timedelta(days=record.offset)
                date_to = date_from + datetime.timedelta(days=record.duration - 1)
                record.date_from = fields.Date.to_string(date_from)
                record.date_to = fields.Date.to_string(date_to)
                record.valid = True
            elif record.mode == MODE_REL and record.type == "w":
                date_from = d - datetime.timedelta(d.weekday())
                date_from = date_from + datetime.timedelta(days=record.offset * 7)
                date_to = date_from + datetime.timedelta(days=(7 * record.duration) - 1)
                record.date_from = fields.Date.to_string(date_from)
                record.date_to = fields.Date.to_string(date_to)
                record.valid = True
            elif record.mode == MODE_REL and record.type == "m":
                date_from = d.replace(day=1)
                date_from = date_from + relativedelta(months=record.offset)
                date_to = (
                    date_from
                    + relativedelta(months=record.duration - 1)
                    + relativedelta(day=31)
                )
                record.date_from = fields.Date.to_string(date_from)
                record.date_to = fields.Date.to_string(date_to)
                record.valid = True
            elif record.mode == MODE_REL and record.type == "y":
                date_from = d.replace(month=1, day=1)
                date_from = date_from + relativedelta(years=record.offset)
                date_to = date_from + relativedelta(years=record.duration - 1)
                date_to = date_to.replace(month=12, day=31)
                record.date_from = fields.Date.to_string(date_from)
                record.date_to = fields.Date.to_string(date_to)
                record.valid = True
            elif record.mode == MODE_REL and record.type == "date_range":
                date_range_obj = record.env["date.range"]
                current_periods = date_range_obj.search(
                    [
                        ("type_id", "=", record.date_range_type_id.id),
                        ("date_start", "<=", d),
                        ("date_end", ">=", d),
                        "|",
                        ("company_id", "=", False),
                        (
                            "company_id",
                            "in",
                            record.report_instance_id.query_company_ids.ids,
                        ),
                    ]
                )
                if current_periods:
                    # TODO we take the first date range we found as current
                    #      this may be surprising if several companies
                    #      have overlapping date ranges with different dates
                    current_period = current_periods[0]
                    all_periods = date_range_obj.search(
                        [
                            ("type_id", "=", current_period.type_id.id),
                            ("company_id", "=", current_period.company_id.id),
                        ],
                        order="date_start",
                    )
                    p = all_periods.ids.index(current_period.id) + record.offset
                    if p >= 0 and p + record.duration <= len(all_periods):
                        periods = all_periods[p : p + record.duration]
                        record.date_from = periods[0].date_start
                        record.date_to = periods[-1].date_end
                        record.valid = True
            if record.mode == MODE_REL and record.valid and record.is_ytd:
                record.date_from = fields.Date.from_string(record.date_to).replace(
                    day=1, month=1
                )

    _name = "mis.report.instance.period"
    _description = "MIS Report Instance Period"

    name = fields.Char(size=32, required=True, string="Label", translate=True)
    mode = fields.Selection(
        [
            (MODE_FIX, "Fixed dates"),
            (MODE_REL, "Relative to report base date"),
            (MODE_NONE, "No date filter"),
        ],
        required=True,
        default=MODE_FIX,
    )
    type = fields.Selection(
        [
            ("d", _("Day")),
            ("w", _("Week")),
            ("m", _("Month")),
            ("y", _("Year")),
            ("date_range", _("Date Range")),
        ],
        string="Period type",
    )
    is_ytd = fields.Boolean(
        default=False,
        string="Year to date",
        help="Forces the start date to Jan 1st of the relevant year",
    )
    date_range_type_id = fields.Many2one(
        comodel_name="date.range.type",
        string="Date Range Type",
        domain=[("allow_overlap", "=", False)],
    )
    offset = fields.Integer(
        string="Offset", help="Offset from current period", default=-1
    )
    duration = fields.Integer(string="Duration", help="Number of periods", default=1)
    date_from = fields.Date(compute="_compute_dates", string="From (computed)")
    date_to = fields.Date(compute="_compute_dates", string="To (computed)")
    manual_date_from = fields.Date(string="From")
    manual_date_to = fields.Date(string="To")
    date_range_id = fields.Many2one(comodel_name="date.range", string="Date Range")
    valid = fields.Boolean(compute="_compute_dates", type="boolean", string="Valid")
    sequence = fields.Integer(string="Sequence", default=100)
    report_instance_id = fields.Many2one(
        comodel_name="mis.report.instance",
        string="Report Instance",
        required=True,
        ondelete="cascade",
    )
    report_id = fields.Many2one(related="report_instance_id.report_id")
    normalize_factor = fields.Integer(
        string="Factor",
        help="Factor to use to normalize the period (used in comparison",
        default=1,
    )
    subkpi_ids = fields.Many2many("mis.report.subkpi", string="Sub KPI Filter")

    source = fields.Selection(
        [
            (SRC_ACTUALS, "Actuals"),
            (SRC_ACTUALS_ALT, "Actuals (alternative)"),
            (SRC_SUMCOL, "Sum columns"),
            (SRC_CMPCOL, "Compare columns"),
        ],
        default=SRC_ACTUALS,
        required=True,
        help="Actuals: current data, from accounting and other queries.\n"
        "Actuals (alternative): current data from an "
        "alternative source (eg a database view providing look-alike "
        "account move lines).\n"
        "Sum columns: summation (+/-) of other columns.\n"
        "Compare to column: compare to other column.\n",
    )
    source_aml_model_id = fields.Many2one(
        comodel_name="ir.model",
        string="Move lines source",
        domain=[
            ("field_id.name", "=", "debit"),
            ("field_id.name", "=", "credit"),
            ("field_id.name", "=", "account_id"),
            ("field_id.name", "=", "date"),
            ("field_id.name", "=", "company_id"),
            ("field_id.model_id.model", "!=", "account.move.line"),
        ],
        help="A 'move line like' model, ie having at least debit, credit, "
        "date, account_id and company_id fields.",
    )
    source_aml_model_name = fields.Char(
        string="Move lines source model name", related="source_aml_model_id.model"
    )
    source_sumcol_ids = fields.One2many(
        comodel_name="mis.report.instance.period.sum",
        inverse_name="period_id",
        string="Columns to sum",
    )
    source_sumcol_accdet = fields.Boolean(string="Sum account details")
    source_cmpcol_from_id = fields.Many2one(
        comodel_name="mis.report.instance.period", string="versus"
    )
    source_cmpcol_to_id = fields.Many2one(
        comodel_name="mis.report.instance.period", string="Compare"
    )
    # filters
    analytic_account_id = fields.Many2one(
        comodel_name="account.analytic.account",
        string="Analytic Account",
        help=(
            "Filter column on journal entries that match this analytic account."
            "This filter is combined with a AND with the report-level filters "
            "and cannot be modified in the preview."
        ),
    )
    analytic_tag_ids = fields.Many2many(
        comodel_name="account.analytic.tag",
        string="Analytic Tags",
        help=(
            "Filter column on journal entries that have all these analytic tags."
            "This filter is combined with a AND with the report-level filters "
            "and cannot be modified in the preview."
        ),
    )

    _order = "sequence, id"

    _sql_constraints = [
        ("duration", "CHECK (duration>0)", "Wrong duration, it must be positive!"),
        (
            "normalize_factor",
            "CHECK (normalize_factor>0)",
            "Wrong normalize factor, it must be positive!",
        ),
        (
            "name_unique",
            "unique(name, report_instance_id)",
            "Period name should be unique by report",
        ),
    ]

    @api.constrains("source_aml_model_id")
    def _check_source_aml_model_id(self):
        for record in self:
            if record.source_aml_model_id:
                record_model = record.source_aml_model_id.field_id.filtered(
                    lambda r: r.name == "account_id"
                ).relation
                report_account_model = record.report_id.account_model
                if record_model != report_account_model:
                    raise ValidationError(
                        _(
                            "Actual (alternative) models used in columns must "
                            "have the same account model in the Account field and must "
                            "be the same defined in the "
                            "report template: %s"
                        )
                        % report_account_model
                    )

    @api.onchange("date_range_id")
    def _onchange_date_range(self):
        if self.date_range_id:
            self.manual_date_from = self.date_range_id.date_start
            self.manual_date_to = self.date_range_id.date_end

    @api.onchange("manual_date_from", "manual_date_to")
    def _onchange_dates(self):
        if self.date_range_id:
            if (
                self.manual_date_from != self.date_range_id.date_start
                or self.manual_date_to != self.date_range_id.date_end
            ):
                self.date_range_id = False

    @api.onchange("source")
    def _onchange_source(self):
        if self.source in (SRC_SUMCOL, SRC_CMPCOL):
            self.mode = MODE_NONE

    def _get_aml_model_name(self):
        self.ensure_one()
        if self.source == SRC_ACTUALS:
            return self.report_id.move_lines_source.model
        elif self.source == SRC_ACTUALS_ALT:
            return self.source_aml_model_name
        return False

    @api.model
    def _get_filter_domain_from_context(self):
        filters = []
        mis_report_filters = self.env.context.get("mis_report_filters", {})
        for filter_name, domain in mis_report_filters.items():
            if domain:
                value = domain.get("value")
                operator = domain.get("operator", "=")
                # Operator = 'all' when coming from JS widget
                if operator == "all":
                    if not isinstance(value, list):
                        value = [value]
                    many_ids = self.report_instance_id.resolve_2many_commands(
                        filter_name, value, ["id"]
                    )
                    for m in many_ids:
                        filters.append((filter_name, "in", [m["id"]]))
                else:
                    filters.append((filter_name, operator, value))
        return filters

    def _get_additional_move_line_filter(self):
        """Prepare a filter to apply on all move lines

        This filter is applied with a AND operator on all
        accounting expression domains. This hook is intended
        to be inherited, and is useful to implement filtering
        on analytic dimensions or operational units.

        The default filter is built from a ``mis_report_filters`` context
        key, which is a list set by the analytic filtering mechanism
        of the mis report widget::

          [(field_name, {'value': value, 'operator': operator})]

        Returns an Odoo domain expression (a python list)
        compatible with account.move.line."""
        self.ensure_one()
        domain = self._get_filter_domain_from_context()
        if (
            self._get_aml_model_name() == "account.move.line"
            and self.report_instance_id.target_move == "posted"
        ):
            domain.extend([("move_id.state", "=", "posted")])
        if self.analytic_account_id:
            domain.append(("analytic_account_id", "=", self.analytic_account_id.id))
        for tag in self.analytic_tag_ids:
            domain.append(("analytic_tag_ids", "=", tag.id))
        return domain

    def _get_additional_query_filter(self, query):
        """Prepare an additional filter to apply on the query

        This filter is combined to the query domain with a AND
        operator. This hook is intended
        to be inherited, and is useful to implement filtering
        on analytic dimensions or operational units.

        Returns an Odoo domain expression (a python list)
        compatible with the model of the query."""
        self.ensure_one()
        return []

    @api.constrains("mode", "source")
    def _check_mode_source(self):
        for rec in self:
            if rec.source in (SRC_ACTUALS, SRC_ACTUALS_ALT):
                if rec.mode == MODE_NONE:
                    raise DateFilterRequired(
                        _("A date filter is mandatory for this source " "in column %s.")
                        % rec.name
                    )
            elif rec.source in (SRC_SUMCOL, SRC_CMPCOL):
                if rec.mode != MODE_NONE:
                    raise DateFilterForbidden(
                        _("No date filter is allowed for this source " "in column %s.")
                        % rec.name
                    )

    @api.constrains("source", "source_cmpcol_from_id", "source_cmpcol_to_id")
    def _check_source_cmpcol(self):
        for rec in self:
            if rec.source == SRC_CMPCOL:
                if not rec.source_cmpcol_from_id or not rec.source_cmpcol_to_id:
                    raise ValidationError(
                        _("Please provide both columns to compare in %s.") % rec.name
                    )
                if rec.source_cmpcol_from_id == rec or rec.source_cmpcol_to_id == rec:
                    raise ValidationError(
                        _("Column %s cannot be compared to itrec.") % rec.name
                    )
                if (
                    rec.source_cmpcol_from_id.report_instance_id
                    != rec.report_instance_id
                    or rec.source_cmpcol_to_id.report_instance_id
                    != rec.report_instance_id
                ):
                    raise ValidationError(
                        _("Columns to compare must belong to the same report " "in %s")
                        % rec.name
                    )


class MisReportInstance(models.Model):
    """The MIS report instance combines everything to compute
    a MIS report template for a set of periods."""

    @api.depends("date")
    def _compute_pivot_date(self):
        for record in self:
            if record.date:
                record.pivot_date = record.date
            else:
                record.pivot_date = fields.Date.context_today(record)

    _name = "mis.report.instance"
    _description = "MIS Report Instance"

    name = fields.Char(required=True, string="Name", translate=True)
    description = fields.Char(related="report_id.description", readonly=True)
    date = fields.Date(
        string="Base date", help="Report base date " "(leave empty to use current date)"
    )
    pivot_date = fields.Date(compute="_compute_pivot_date", string="Pivot date")
    report_id = fields.Many2one("mis.report", required=True, string="Report")
    period_ids = fields.One2many(
        comodel_name="mis.report.instance.period",
        inverse_name="report_instance_id",
        required=True,
        string="Periods",
        copy=True,
    )
    target_move = fields.Selection(
        [("posted", "All Posted Entries"), ("all", "All Entries")],
        string="Target Moves",
        required=True,
        default="posted",
    )
    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
        default=lambda self: self.env.company,
        required=True,
    )
    multi_company = fields.Boolean(
        string="Multiple companies",
        help="Check if you wish to specify "
        "children companies to be searched for data.",
        default=False,
    )
    company_ids = fields.Many2many(
        comodel_name="res.company",
        string="Companies",
        help="Select companies for which data will be searched.",
    )
    query_company_ids = fields.Many2many(
        comodel_name="res.company",
        compute="_compute_query_company_ids",
        help="Companies for which data will be searched.",
    )
    currency_id = fields.Many2one(
        comodel_name="res.currency",
        string="Currency",
        help="Select target currency for the report. "
        "Required if companies have different currencies.",
        required=False,
    )
    landscape_pdf = fields.Boolean(string="Landscape PDF")
    no_auto_expand_accounts = fields.Boolean(string="Disable account details expansion")
    display_columns_description = fields.Boolean(
        help="Display the date range details in the column headers."
    )
    comparison_mode = fields.Boolean(
        compute="_compute_comparison_mode", inverse="_inverse_comparison_mode"
    )
    date_range_id = fields.Many2one(comodel_name="date.range", string="Date Range")
    date_from = fields.Date(string="From")
    date_to = fields.Date(string="To")
    temporary = fields.Boolean(default=False)
    analytic_account_id = fields.Many2one(
        comodel_name="account.analytic.account", string="Analytic Account"
    )
    analytic_tag_ids = fields.Many2many(
        comodel_name="account.analytic.tag", string="Analytic Tags"
    )
    hide_analytic_filters = fields.Boolean(default=True)

    @api.onchange("company_id", "multi_company")
    def _onchange_company(self):
        if self.company_id and self.multi_company:
            self.company_ids = self.env["res.company"].search(
                [("id", "child_of", self.company_id.id)]
            )
        else:
            self.company_ids = False

    @api.depends("multi_company", "company_id", "company_ids")
    def _compute_query_company_ids(self):
        for rec in self:
            if rec.multi_company:
                rec.query_company_ids = rec.company_ids or rec.company_id
            else:
                rec.query_company_ids = rec.company_id

    @api.model
    def get_filter_descriptions_from_context(self):
        filters = self.env.context.get("mis_report_filters", {})
        analytic_account_id = filters.get("analytic_account_id", {}).get("value")
        filter_descriptions = []
        if analytic_account_id:
            analytic_account = self.env["account.analytic.account"].browse(
                analytic_account_id
            )
            filter_descriptions.append(
                _("Analytic Account: %s") % analytic_account.display_name
            )
        analytic_tag_value = filters.get("analytic_tag_ids", {}).get("value")
        if analytic_tag_value:
            analytic_tag_names = self.resolve_2many_commands(
                "analytic_tag_ids", analytic_tag_value, ["name"]
            )
            filter_descriptions.append(
                _("Analytic Tags: %s")
                % ", ".join([rec["name"] for rec in analytic_tag_names])
            )
        return filter_descriptions

    def save_report(self):
        self.ensure_one()
        self.write({"temporary": False})
        action = self.env.ref("mis_builder.mis_report_instance_view_action")
        res = action.read()[0]
        view = self.env.ref("mis_builder.mis_report_instance_view_form")
        res.update({"views": [(view.id, "form")], "res_id": self.id})
        return res

    @api.model
    def _vacuum_report(self, hours=24):
        clear_date = fields.Datetime.to_string(
            datetime.datetime.now() - datetime.timedelta(hours=hours)
        )
        reports = self.search(
            [("write_date", "<", clear_date), ("temporary", "=", True)]
        )
        _logger.debug("Vacuum %s Temporary MIS Builder Report", len(reports))
        return reports.unlink()

    def copy(self, default=None):
        self.ensure_one()
        default = dict(default or {})
        default["name"] = _("%s (copy)") % self.name
        return super(MisReportInstance, self).copy(default)

    def _format_date(self, date):
        # format date following user language
        lang_model = self.env["res.lang"]
        lang = lang_model._lang_get(self.env.user.lang)
        date_format = lang.date_format
        return datetime.datetime.strftime(fields.Date.from_string(date), date_format)

    @api.depends("date_from")
    def _compute_comparison_mode(self):
        for instance in self:
            instance.comparison_mode = bool(instance.period_ids) and not bool(
                instance.date_from
            )

    def _inverse_comparison_mode(self):
        for record in self:
            if not record.comparison_mode:
                if not record.date_from:
                    record.date_from = fields.Date.context_today(self)
                if not record.date_to:
                    record.date_to = fields.Date.context_today(self)
                record.period_ids.unlink()
                record.write({"period_ids": [(0, 0, {"name": "Default"})]})
            else:
                record.date_from = None
                record.date_to = None

    @api.onchange("date_range_id")
    def _onchange_date_range(self):
        if self.date_range_id:
            self.date_from = self.date_range_id.date_start
            self.date_to = self.date_range_id.date_end

    @api.onchange("date_from", "date_to")
    def _onchange_dates(self):
        if self.date_range_id:
            if (
                self.date_from != self.date_range_id.date_start
                or self.date_to != self.date_range_id.date_end
            ):
                self.date_range_id = False

    def _add_analytic_filters_to_context(self, context):
        self.ensure_one()
        if self.analytic_account_id:
            context["mis_report_filters"]["analytic_account_id"] = {
                "value": self.analytic_account_id.id,
                "operator": "=",
            }
        if self.analytic_tag_ids:
            context["mis_report_filters"]["analytic_tag_ids"] = {
                "value": self.analytic_tag_ids.ids,
                "operator": "all",
            }

    def _context_with_filters(self):
        self.ensure_one()
        if "mis_report_filters" in self.env.context:
            # analytic filters are already in context, do nothing
            return self.env.context
        context = dict(self.env.context, mis_report_filters={})
        self._add_analytic_filters_to_context(context)
        return context

    def preview(self):
        self.ensure_one()
        view_id = self.env.ref("mis_builder." "mis_report_instance_result_view_form")
        return {
            "type": "ir.actions.act_window",
            "res_model": "mis.report.instance",
            "res_id": self.id,
            "view_mode": "form",
            "view_id": view_id.id,
            "target": "current",
            "context": self._context_with_filters(),
        }

    def print_pdf(self):
        self.ensure_one()
        context = dict(self._context_with_filters(), landscape=self.landscape_pdf)
        return (
            self.env.ref("mis_builder.qweb_pdf_export")
            .with_context(context)
            .report_action(self, data=dict(dummy=True))  # required to propagate context
        )

    def export_xls(self):
        self.ensure_one()
        context = dict(self._context_with_filters())
        return (
            self.env.ref("mis_builder.xls_export")
            .with_context(context)
            .report_action(self, data=dict(dummy=True))  # required to propagate context
        )

    def display_settings(self):
        assert len(self.ids) <= 1
        view_id = self.env.ref("mis_builder.mis_report_instance_view_form")
        return {
            "type": "ir.actions.act_window",
            "res_model": "mis.report.instance",
            "res_id": self.id if self.id else False,
            "view_mode": "form",
            "views": [(view_id.id, "form")],
            "view_id": view_id.id,
            "target": "current",
        }

    def _add_column_move_lines(self, aep, kpi_matrix, period, label, description):
        if not period.date_from or not period.date_to:
            raise UserError(
                _("Column %s with move lines source must have from/to dates.")
                % (period.name,)
            )
        expression_evaluator = ExpressionEvaluator(
            aep,
            period.date_from,
            period.date_to,
            None,  # target_move now part of additional_move_line_filter
            period._get_additional_move_line_filter(),
            period._get_aml_model_name(),
        )
        self.report_id._declare_and_compute_period(
            expression_evaluator,
            kpi_matrix,
            period.id,
            label,
            description,
            period.subkpi_ids,
            period._get_additional_query_filter,
            no_auto_expand_accounts=self.no_auto_expand_accounts,
        )

    def _add_column_sumcol(self, aep, kpi_matrix, period, label, description):
        kpi_matrix.declare_sum(
            period.id,
            [(c.sign, c.period_to_sum_id.id) for c in period.source_sumcol_ids],
            label,
            description,
            period.source_sumcol_accdet,
        )

    def _add_column_cmpcol(self, aep, kpi_matrix, period, label, description):
        kpi_matrix.declare_comparison(
            period.id,
            period.source_cmpcol_to_id.id,
            period.source_cmpcol_from_id.id,
            label,
            description,
        )

    def _add_column(self, aep, kpi_matrix, period, label, description):
        if period.source == SRC_ACTUALS:
            return self._add_column_move_lines(
                aep, kpi_matrix, period, label, description
            )
        elif period.source == SRC_ACTUALS_ALT:
            return self._add_column_move_lines(
                aep, kpi_matrix, period, label, description
            )
        elif period.source == SRC_SUMCOL:
            return self._add_column_sumcol(aep, kpi_matrix, period, label, description)
        elif period.source == SRC_CMPCOL:
            return self._add_column_cmpcol(aep, kpi_matrix, period, label, description)

    def _compute_matrix(self):
        """Compute a report and return a KpiMatrix.

        The key attribute of the matrix columns (KpiMatrixCol)
        is guaranteed to be the id of the mis.report.instance.period.
        """
        self.ensure_one()
        aep = self.report_id._prepare_aep(self.query_company_ids, self.currency_id)
        kpi_matrix = self.report_id.prepare_kpi_matrix(self.multi_company)
        for period in self.period_ids:
            description = None
            if period.mode == MODE_NONE:
                pass
            elif not self.display_columns_description:
                pass
            elif period.date_from == period.date_to and period.date_from:
                description = self._format_date(period.date_from)
            elif period.date_from and period.date_to:
                date_from = self._format_date(period.date_from)
                date_to = self._format_date(period.date_to)
                description = _("from %s to %s") % (date_from, date_to)
            self._add_column(aep, kpi_matrix, period, period.name, description)
        kpi_matrix.compute_comparisons()
        kpi_matrix.compute_sums()
        return kpi_matrix

    def compute(self):
        self.ensure_one()
        kpi_matrix = self._compute_matrix()
        return kpi_matrix.as_dict()

    def drilldown(self, arg):
        self.ensure_one()
        period_id = arg.get("period_id")
        expr = arg.get("expr")
        account_id = arg.get("account_id")
        if period_id and expr and AEP.has_account_var(expr):
            period = self.env["mis.report.instance.period"].browse(period_id)
            aep = AEP(
                self.query_company_ids, self.currency_id, self.report_id.account_model
            )
            aep.parse_expr(expr)
            aep.done_parsing()
            domain = aep.get_aml_domain_for_expr(
                expr,
                period.date_from,
                period.date_to,
                None,  # target_move now part of additional_move_line_filter
                account_id,
            )
            domain.extend(period._get_additional_move_line_filter())
            return {
                "name": u"{} - {}".format(expr, period.name),
                "domain": domain,
                "type": "ir.actions.act_window",
                "res_model": period._get_aml_model_name(),
                "views": [[False, "list"], [False, "form"]],
                "view_mode": "list",
                "target": "current",
                "context": {"active_test": False},
            }
        else:
            return False
