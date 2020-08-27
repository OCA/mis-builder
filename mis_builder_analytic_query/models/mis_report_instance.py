# Copyright 2020 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, fields, models
from odoo.exceptions import UserError


class MisReportQuery(models.Model):
    _inherit = "mis.report.query"

    analytic_account_field_id = fields.Many2one(
        "ir.model.fields", string="Model Analytic Account"
    )
    parent_model_id = fields.Many2one(
        "ir.model", string="Parent Model", ondelete="restrict"
    )
    analytic_account_parent_field_id = fields.Many2one(
        "ir.model.fields",
        string="Parent Model Analytic Account",
        help="Alternative of analytic account on model if not exist",
    )


class MisReportInstancePeriod(models.Model):
    _inherit = "mis.report.instance.period"

    def _get_additional_query_filter(self, query):
        self.ensure_one()
        res = super(MisReportInstancePeriod, self)._get_additional_query_filter(
            query=query
        )
        if query.analytic_account_field_id or query.analytic_account_parent_field_id:
            if self._context.get("mis_report_filters", False) and self._context[
                "mis_report_filters"
            ].get("analytic_account_id", False):
                analytic_dict = self._context["mis_report_filters"][
                    "analytic_account_id"
                ]
                if query.analytic_account_field_id:
                    analytic_field_name = query.analytic_account_field_id.name
                else:
                    model = self.env[query.model_id.model]
                    model_fields = model.fields_get()
                    relation_field_name = False
                    for field in model_fields:
                        if (
                            model_fields[field].get("relation", False)
                            == query.parent_model_id.model
                            and model_fields[field].get("type", False) == "many2one"
                        ):
                            relation_field_name = field
                            break
                    if not relation_field_name:
                        raise UserError(
                            _(
                                "Relational field not found for model %s"
                                % query.parent_model_id.name
                            )
                        )
                    analytic_field_name = ".".join(
                        [
                            relation_field_name,
                            query.analytic_account_parent_field_id.name,
                        ]
                    )
                res.append(
                    (
                        analytic_field_name,
                        analytic_dict.get("operator", False),
                        analytic_dict.get("value", False),
                    )
                )
        return res
