# Copyright 2025 - TODAY, Wesley Oliveira <wesley.oliveira@escodoo.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class MisReport(models.Model):

    _inherit = "mis.report"

    bi_sql_view = fields.Many2one(
        string="BI SQL View",
        comodel_name="bi.sql.view",
        domain=[("mis_builder_activated", "=", True)],
    )
    bi_sql_view_required = fields.Boolean(
        default=False, compute="_compute_bi_sql_view_required"
    )

    @api.depends("move_lines_source")
    def _compute_bi_sql_view_required(self):
        for record in self:
            model_id = (
                self.env["ir.model"]
                .search([("model", "=", "mis.builder.bi.sql.line")])
                .id
            )
            record.bi_sql_view_required = record.move_lines_source.id == model_id
