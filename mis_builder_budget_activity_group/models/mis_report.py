# Copyright 2021 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models

from .aep import AccountingExpressionProcessorActivity as AEPA


class MisReport(models.Model):
    _inherit = "mis.report"

    is_activity = fields.Boolean(
        help="if check, Expression will compute Activity instead Account"
    )

    @api.depends("move_lines_source")
    def _compute_account_model(self):
        super()._compute_account_model()
        for record in self:
            if record.is_activity:
                record.account_model = "budget.activity"

    def _prepare_aep(self, companies, currency=None):
        self.ensure_one()
        if self.is_activity:
            aep = AEPA(companies, currency, self.account_model)
            for kpi in self.all_kpi_ids:
                kpi.expression_ids.flush()
                for expression in kpi.expression_ids:
                    if expression.name:
                        aep.parse_expr(expression.name)
            aep.done_parsing()
        else:
            aep = super()._prepare_aep(companies, currency)
        return aep
