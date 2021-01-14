# Copyright 2021 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.addons.mis_builder.models.expression_evaluator import ExpressionEvaluator


class ExpressionEvaluatorActivity(ExpressionEvaluator):
    def __init__(
        self,
        aep,
        date_from,
        date_to,
        target_move=None,
        additional_move_line_filter=None,
        aml_model=None,
        is_activity=False,
    ):
        super().__init__(
            aep, date_from, date_to, target_move, additional_move_line_filter, aml_model
        )
        self.is_activity = is_activity

    def aep_do_queries(self):
        if self.aep and not self._aep_queries_done:
            if self.is_activity:
                self.aep.do_queries(
                    self.date_from,
                    self.date_to,
                    self.target_move,
                    self.additional_move_line_filter,
                    self.aml_model,
                    self.is_activity,
                )
                self._aep_queries_done = True
            else:
                super().aep_do_queries()
