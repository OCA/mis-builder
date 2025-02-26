# Copyright 2025 - TODAY, Wesley Oliveira <wesley.oliveira@escodoo.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class BiSQLView(models.Model):

    _inherit = "bi.sql.view"

    mis_builder_compatible = fields.Boolean(
        compute="_compute_mis_builder_compatible",
        default=False,
    )
    mis_builder_activated = fields.Boolean(default=False)

    @api.depends()
    def _compute_mis_builder_compatible(self):
        compatible = True
        model_sql_fields = self.bi_sql_view_field_ids
        credit_field = model_sql_fields.filtered(
            lambda x: x.name == "x_credit" and x.ttype == "float"
        )
        debit_field = model_sql_fields.filtered(
            lambda x: x.name == "x_debit" and x.ttype == "float"
        )
        account_field = model_sql_fields.filtered(
            lambda x: x.name == "x_account_id" and x.ttype == "many2one"
        )
        date_field = model_sql_fields.filtered(
            lambda x: x.name == "x_date" and x.ttype == "date"
        )
        company_field = model_sql_fields.filtered(
            lambda x: x.name == "x_company_id" and x.ttype == "many2one"
        )
        analytic_account_field = model_sql_fields.filtered(
            lambda x: x.name == "x_analytic_account_id" and x.ttype == "many2one"
        )

        if (
            not credit_field
            or not debit_field
            or not account_field
            or account_field.many2one_model_id.model != "account.account"
            or not date_field
            or not company_field
            or company_field.many2one_model_id.model != "res.company"
            or (
                analytic_account_field
                and analytic_account_field.many2one_model_id.model
                != "account.analytic.account"
            )
        ):
            compatible = False

        self.mis_builder_compatible = compatible

    def activate_mis_builder(self):
        if self.mis_builder_compatible:
            model_id = (
                self.env["ir.model"]
                .search([("model", "=", "mis.builder.bi.sql.line")])
                .id
            )
            self.env["ir.model.fields"].create(
                {
                    "name": self.view_name,
                    "model_id": model_id,
                    "state": "manual",
                    "ttype": "many2one",
                    "relation": self.model_name,
                }
            )
            self.mis_builder_activated = True

    def remove_mis_builder(self):
        if self.mis_builder_compatible and self.mis_builder_activated:
            self.env["mis.builder.bi.sql.line"].search(
                [("bi_sql_model", "=", self.model_id.id)]
            ).unlink()

            model_id = (
                self.env["ir.model"]
                .search([("model", "=", "mis.builder.bi.sql.line")])
                .id
            )
            self.env["ir.model.fields"].search(
                [
                    ("name", "=", self.view_name),
                    ("model_id", "=", model_id),
                ]
            ).unlink()

            self.mis_builder_activated = False

    def button_set_draft(self):
        if self.mis_builder_activated:
            self.remove_mis_builder()
        return super().button_set_draft()

    def button_refresh_materialized_view(self):
        super().button_refresh_materialized_view()
        if self.mis_builder_activated:
            model = self.env["mis.builder.bi.sql.line"]
            model._create_mis_builder_bi_sql_lines()

    def copy(self, default=None):
        self.ensure_one()
        default = dict(default or {})
        default["mis_builder_activated"] = False
        return super().copy(default)
