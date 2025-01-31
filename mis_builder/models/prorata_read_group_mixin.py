# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from collections import defaultdict
from itertools import chain

from odoo import api, fields, models
from odoo.exceptions import UserError
from odoo.fields import Date

from .mis_kpi_data import intersect_days
from .simple_array import SimpleArray


class ProRataReadGroupMixin(models.AbstractModel):
    _name = "prorata.read_group.mixin"
    _description = "Adapt model with date_from/date_to for pro-rata temporis read_group"

    date_from = fields.Date(required=True)
    date_to = fields.Date(required=True)
    date = fields.Date(
        compute=lambda self: None,
        search="_search_date",
        help=(
            "Dummy field that adapts searches on date to searches on date_from/date_to."
        ),
    )

    def _search_date(self, operator, value):
        if operator in (">=", ">"):
            return [("date_to", operator, value)]
        elif operator in ("<=", "<"):
            return [("date_from", operator, value)]
        raise UserError(
            self.env._("Unsupported operator %s for searching on date", operator)
        )

    @api.model
    def _intersect_days(self, item_dt_from, item_dt_to, dt_from, dt_to):
        return intersect_days(item_dt_from, item_dt_to, dt_from, dt_to)

    @api.model
    def _prorata(self, item, dt_from, dt_to, sum_field):
        if sum_field == "__count":
            return 1
        item_dt_from = Date.from_string(item["date_from"])
        item_dt_to = Date.from_string(item["date_to"])
        i_days, item_days = self._intersect_days(
            item_dt_from, item_dt_to, dt_from, dt_to
        )
        return item[sum_field] * i_days / item_days

    @api.model
    def _read_group(
        self,
        domain,
        groupby=(),
        aggregates=(),
        having=(),
        offset=0,
        limit=None,
        order=None,
    ):
        """Override _read_group to perform pro-rata temporis adjustments.

        When _read_group is invoked with a domain that filters on
        a time period (date >= from and date <= to, or
        date_from <= to and date_to >= from), adjust the accumulated
        values pro-rata temporis.

        This mechanism works in specific cases and is primarily designed to
        make AEP work with budget tables.
        """
        date_from = None
        date_to = None
        assert isinstance(domain, list)
        for domain_item in domain:
            if isinstance(domain_item, list | tuple):
                field, op, value = domain_item
                if field == "date" and op == ">=":
                    date_from = value
                elif field == "date_to" and op == ">=":
                    date_from = value
                elif field == "date" and op == "<=":
                    date_to = value
                elif field == "date_from" and op == "<=":
                    date_to = value
        if (
            date_from is not None
            and date_to is not None
            and all(a.endswith(":sum") or a == "__count" for a in aggregates)
            and not any(":" in g for g in groupby)
        ):
            dt_from = Date.from_string(date_from)
            dt_to = Date.from_string(date_to)
            stripped_aggregates = [a.rstrip(":sum") for a in aggregates]
            sum_fields = filter(lambda a: a != "__count", stripped_aggregates)
            read_fields = [*groupby, *sum_fields, "date_from", "date_to"]
            # res is a dictionary with a tuple of groupby field names as keys,
            # and sums of aggregate fields as values.
            res = defaultdict(lambda: SimpleArray((0.0,) * len(aggregates)))
            for item in self.search_fetch(domain, read_fields):
                key = tuple(item[k] for k in groupby)
                res[key] += SimpleArray(
                    self._prorata(item, dt_from, dt_to, f) for f in stripped_aggregates
                )
            return [tuple(chain(k, v)) for k, v in res.items()]
        return super()._read_group(
            domain,
            groupby,
            aggregates,
            having,
            offset,
            limit,
            order,
        )
