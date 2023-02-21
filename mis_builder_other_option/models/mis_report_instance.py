from odoo import api, models
from odoo.tools import date_utils

from odoo.addons.mis_builder.models.aep import AccountingExpressionProcessor as AEP
from odoo.addons.mis_builder.models.mis_report_instance import MODE_REL

PERIOD_TYPES = {
    "d": "day",
    "w": "week",
    "m": "month",
    "y": "year",
}


class MisReportInstancePeriod(models.Model):
    _inherit = "mis.report.instance.period"

    @api.depends_context("period_offset", "period_range")
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
        super()._compute_dates()

        # Recompute dates with offset or change in range
        if (
            self.env.context.get("period_offset", 0) != 0
            or self.env.context.get("period_range", 1) > 1
        ):
            period_offset = self.env.context.get("period_offset", 0)
            period_range = self.env.context.get("period_range", 1) - 1
            for period in self.filtered(
                lambda p: p.date_from and p.date_to and not p.is_ytd
            ):
                if period.mode == MODE_REL and period.type in PERIOD_TYPES.keys():
                    qty = period.duration * (period_offset - period_range)
                    granularity = PERIOD_TYPES[period.type]
                else:
                    diff = (period.date_to - period.date_from).days + 1
                    qty = diff * (period_offset - period_range)
                    granularity = "day"

                period.date_from += date_utils.get_timedelta(qty, granularity)
                if period_offset:
                    date_to = period.date_to + date_utils.get_timedelta(
                        qty, granularity
                    )
                    period.date_to = date_utils.end_of(date_to, granularity)


class MisReportInstance(models.Model):
    _inherit = "mis.report.instance"

    """
    Code taken from
        mis_builder/models/mis_report_instance.py
    as of

commit cd7990901b51b73c8ef7dc105a5b4e392384463d
Date:   Mon Feb 13 19:16:49 2023 +0000

    We make the original point to this, and then make sure the super
    is calling the correct super!
    """

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

            # Inserted
            # ==========================================================================
            period = period.with_context(aep.mis_options)
            # ==========================================================================

            domain = aep.get_aml_domain_for_expr(
                expr,
                period.date_from,
                period.date_to,
                account_id,
            )
            domain.extend(period._get_additional_move_line_filter())
            return {
                "name": self._get_drilldown_action_name(arg),
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
