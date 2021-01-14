# Copyright 2021 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import ast

from odoo import api, fields, models


class MisReportKpi(models.Model):
    _inherit = "mis.report.kpi"

    activity_expression = fields.Boolean(
        compute="_compute_is_activity",
        readonly=False,
        store=True,
    )
    budget_activity_group = fields.Many2one(
        comodel_name="budget.activity.group",
        string="Activity Group",
    )
    respectively_variation = fields.Char(
        help="respectively variation over the "
        "period (p), initial balance (i), ending balance (e)"
    )

    @api.depends("report_id.is_activity")
    def _compute_is_activity(self):
        self.ensure_one()
        self.activity_expression = self.report_id.is_activity

    @api.depends(
        "expression_ids.subkpi_id.name",
        "expression_ids.name",
        "budget_activity_group.activity_ids",
    )
    def _compute_expression(self):
        super()._compute_expression()
        for kpi in self:
            if kpi.activity_expression and kpi.budget_activity_group:
                activity_ids = kpi.budget_activity_group.activity_ids
                account_ids = activity_ids.mapped("account_id")
                account_str = [ast.literal_eval(acc.code) for acc in account_ids]
                kpi.expression = "bal{}{}[('activity_id', 'in', {})]".format(
                    kpi.respectively_variation or "",
                    account_str,
                    tuple(activity_ids.ids),
                )
                # Update expression_ids for display realtime
                kpi._inverse_expression()
