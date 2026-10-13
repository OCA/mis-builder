# Copyright 2026 KMEE
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, models


class AccountAnalyticPlan(models.Model):
    _inherit = "account.analytic.plan"

    def _mis_analytic_refresh_view(self):
        # each root plan is a column of account_analytic_line: creating, moving or
        # removing a plan adds or drops a column (DROP COLUMN ... CASCADE also drops
        # the view), so the view is rebuilt afterwards
        self.env["mis.analytic.move.line"].init()

    @api.model_create_multi
    def create(self, vals_list):
        plans = super().create(vals_list)
        self._mis_analytic_refresh_view()
        return plans

    def write(self, vals):
        res = super().write(vals)
        if {"parent_id", "name"} & set(vals):
            self._mis_analytic_refresh_view()
        return res

    def unlink(self):
        res = super().unlink()
        self._mis_analytic_refresh_view()
        return res
