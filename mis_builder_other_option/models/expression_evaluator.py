from odoo.addons.mis_builder.models.expression_evaluator import (
    ExpressionEvaluator as OriginalExpressionEvaluator,
)
from odoo.addons.mis_builder.models.mis_safe_eval import NameDataError, mis_safe_eval


class ExpressionEvaluator(OriginalExpressionEvaluator):
    """
    Code taken from
        mis_builder/models/expression_evaluator.py
    as of

    commit cd7990901b51b73c8ef7dc105a5b4e392384463d
    Date:   Mon Feb 13 19:16:49 2023 +0000

    We make the original point to this, and then make sure the super
    is calling the correct super!
    """

    def eval_expressions_modified(self, expressions, locals_dict):
        vals = []
        drilldown_args = []
        name_error = False
        for expression in expressions:
            expr = expression and expression.name or "AccountingNone"

            # Inserted
            # ==========================================================================
            # Recompute AEP when offsetting period or changing the range
            aep = self.aep
            for mo in self.aep._ACC_RE.finditer(expr):
                field, mode, account_sel, ml_domain, options = mo.groups()
                mis_options = options and mis_safe_eval(options, {}) or {}
                if mis_options.get("period_offset") or mis_options.get("period_range"):
                    period = locals_dict["period"].with_context(mis_options)
                    aep.do_queries(
                        period.date_from,
                        period.date_to,
                        self.additional_move_line_filter,
                        self.aml_model,
                    )
            # ==========================================================================

            # Modified
            # ==========================================================================
            # if self.aep:
            #    replaced_expr = self.aep:.replace_expr(expr)
            if aep:
                replaced_expr = aep.replace_expr(expr)
            # ==========================================================================
            else:
                replaced_expr = expr
            val = mis_safe_eval(replaced_expr, locals_dict)
            vals.append(val)
            if isinstance(val, NameDataError):
                name_error = True
            if replaced_expr != expr:
                drilldown_args.append({"expr": expr})
            else:
                drilldown_args.append(None)
        return vals, drilldown_args, name_error


OriginalExpressionEvaluator.eval_expressions = (
    ExpressionEvaluator.eval_expressions_modified
)
