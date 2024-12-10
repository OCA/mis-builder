# Copyright 2017 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class MisReportKpiExpression(models.Model):
    _inherit = "mis.report.kpi.expression"

    @api.model
    def _search_display_name(self, operator, value):
        domain = super()._search_display_name(operator, value)

        if "default_budget_id" in self.env.context:
            report_id = (
                self.env["mis.budget"]
                .browse(self.env.context["default_budget_id"])
                .report_id.id
            )
            if report_id:
                domain += [("kpi_id.report_id", "=", report_id)]
                if "." in value:
                    domain += [("subkpi_id.report_id", "=", report_id)]
        return domain
