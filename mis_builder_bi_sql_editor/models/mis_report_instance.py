# Copyright 2025 - TODAY, Wesley Oliveira <wesley.oliveira@escodoo.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class MisReportInstancePeriod(models.Model):

    _inherit = "mis.report.instance.period"

    bi_sql_view = fields.Many2one(
        string="BI SQL View",
        comodel_name="bi.sql.view",
        domain=[("mis_builder_activated", "=", True)],
    )
    bi_sql_view_required = fields.Boolean(
        default=False, compute="_compute_bi_sql_view_required"
    )

    @api.depends("source", "source_aml_model_id")
    def _compute_bi_sql_view_required(self):
        for record in self:
            if record.source == "actuals_alt":
                model_id = (
                    self.env["ir.model"]
                    .search([("model", "=", "mis.builder.bi.sql.line")])
                    .id
                )
                record.bi_sql_view_required = record.source_aml_model_id.id == model_id
            else:
                record.bi_sql_view_required = False

    def _get_additional_move_line_filter(self):
        context = self.env.context
        if self.bi_sql_view:
            context["mis_report_filters"]["bi_sql_model"] = {
                "value": self.bi_sql_view.model_id.id,
                "operator": "=",
            }
        return super()._get_additional_move_line_filter()


class MisReportInstance(models.Model):

    _inherit = "mis.report.instance"

    bi_sql_view = fields.Many2one(
        string="BI SQL View",
        comodel_name="bi.sql.view",
        related="report_id.bi_sql_view",
    )

    def _context_with_filters(self):
        context = super()._context_with_filters()
        if self.bi_sql_view:
            context["mis_report_filters"]["bi_sql_model"] = {
                "value": self.bi_sql_view.model_id.id,
                "operator": "=",
            }
        return context
