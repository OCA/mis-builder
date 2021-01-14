# Copyright 2021 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import _, models
from odoo.exceptions import UserError
from odoo.osv.expression import AND

from odoo.addons.mis_builder_budget.models.mis_report_instance import (
    MisBudgetAwareExpressionEvaluator,
)

from .aep import AccountingExpressionProcessorActivity as AEPA
from .expression_evaluator import ExpressionEvaluatorActivity


class MisBudgetAwareExpressionEvaluatorActivity(MisBudgetAwareExpressionEvaluator):
    def __init__(
        self,
        date_from,
        date_to,
        kpi_data,
        additional_move_line_filter,
        is_activity=False,
    ):
        super().__init__(date_from, date_to, kpi_data, additional_move_line_filter)
        self.is_activity = is_activity


class MisReportInstance(models.Model):
    _inherit = "mis.report.instance"

    def _add_column_mis_budget(self, aep, kpi_matrix, period, label, description):
        # fetch budget data for the period
        base_domain = AND(
            [
                [("budget_id", "=", period.source_mis_budget_id.id)],
                period._get_additional_budget_item_filter(),
            ]
        )
        kpi_data = self.env["mis.budget.item"]._query_kpi_data(
            period.date_from, period.date_to, base_domain
        )
        expression_evaluator = MisBudgetAwareExpressionEvaluatorActivity(
            period.date_from,
            period.date_to,
            kpi_data,
            period._get_additional_move_line_filter(),
            self.report_id.is_activity,
        )
        return self.report_id._declare_and_compute_period(
            expression_evaluator,
            kpi_matrix,
            period.id,
            label,
            description,
            period.subkpi_ids,
            period._get_additional_query_filter,
            no_auto_expand_accounts=self.no_auto_expand_accounts,
        )

    def _add_column_move_lines(self, aep, kpi_matrix, period, label, description):
        if not period.date_from or not period.date_to:
            raise UserError(
                _("Column %s with move lines source must have from/to dates.")
                % (period.name,)
            )
        expression_evaluator = ExpressionEvaluatorActivity(
            aep,
            period.date_from,
            period.date_to,
            None,  # target_move now part of additional_move_line_filter
            period._get_additional_move_line_filter(),
            period._get_aml_model_name(),
            self.report_id.is_activity,
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

    def drilldown(self, arg):
        self.ensure_one()
        if self.report_id.is_activity:
            period_id = arg.get("period_id")
            expr = arg.get("expr")
            account_id = arg.get("account_id")
            if period_id and expr and AEPA.has_account_var(expr):
                period = self.env["mis.report.instance.period"].browse(period_id)
                aep = AEPA(
                    self.query_company_ids,
                    self.currency_id,
                    self.report_id.account_model,
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
                    "name": self._get_drilldown_action_name(arg),
                    "domain": domain,
                    "type": "ir.actions.act_window",
                    "res_model": period._get_aml_model_name(),
                    "views": [[False, "list"], [False, "form"]],
                    "view_mode": "list",
                    "target": "current",
                    "context": {"active_test": False},
                }
        return super().drilldown(arg)
