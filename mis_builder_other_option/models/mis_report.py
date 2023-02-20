from odoo import models


class MisReport(models.Model):
    _inherit = "mis.report"

    def _declare_and_compute_col(
        self,
        expression_evaluator,
        kpi_matrix,
        col_key,
        col_label,
        col_description,
        subkpis_filter,
        locals_dict,
        no_auto_expand_accounts=False,
    ):
        locals_dict["period"] = self.env["mis.report.instance.period"].browse(col_key)

        return super()._declare_and_compute_col(
            expression_evaluator,
            kpi_matrix,
            col_key,
            col_label,
            col_description,
            subkpis_filter,
            locals_dict,
            no_auto_expand_accounts=no_auto_expand_accounts,
        )
