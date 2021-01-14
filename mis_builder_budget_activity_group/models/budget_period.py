# Copyright 2021 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, models


class BudgetPeriod(models.Model):
    _inherit = "budget.period"

    def _prepare_controls_activity(self, budget_period, budget_moves):
        controls = set()
        control_analytics = budget_period.control_analytic_account_ids
        for i in budget_moves:
            if budget_period.control_all_analytic_accounts:
                if i.analytic_account_id and i.activity_id:
                    controls.add((i.analytic_account_id.id, i.activity_id.id))
            else:  # Only analtyic in control
                if i.analytic_account_id in control_analytics and i.activity_id:
                    controls.add((i.analytic_account_id.id, i.activity_id.id))
        return controls

    @api.model
    def _prepare_controls(self, budget_period, budget_moves):
        if budget_period.report_id.is_activity:
            return self._prepare_controls_activity(budget_period, budget_moves)
        return super()._prepare_controls(budget_period, budget_moves)
