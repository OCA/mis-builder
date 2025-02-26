# Copyright 2025 - TODAY, Wesley Oliveira <wesley.oliveira@escodoo.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class MisBuilderBiSqlLine(models.Model):
    _name = "mis.builder.bi.sql.line"
    _description = "MIS Builder BI SQL Line"

    credit = fields.Float()
    debit = fields.Float()
    account_id = fields.Many2one(comodel_name="account.account")
    date = fields.Date()
    company_id = fields.Many2one(comodel_name="res.company")
    analytic_account_id = fields.Many2one(comodel_name="account.analytic.account")
    bi_sql_model = fields.Many2one(comodel_name="ir.model")
    res_id = fields.Integer()

    def _create_mis_builder_bi_sql_lines(self):
        sql_view_ids = self.env["bi.sql.view"].search(
            [
                ("mis_builder_compatible", "=", True),
                ("mis_builder_activated", "=", True),
            ]
        )
        for sql_view in sql_view_ids:
            res = self.env[sql_view.model_id.model].search([])
            for line in res:
                mis_sql_line = self.env["mis.builder.bi.sql.line"].search(
                    [
                        ("bi_sql_model", "=", sql_view.model_id.id),
                        ("res_id", "=", line.id),
                    ],
                    limit=1,
                )
                if not mis_sql_line:
                    vals = {
                        "credit": line.x_credit,
                        "debit": line.x_debit,
                        "account_id": line.x_account_id.id,
                        "date": line.x_date,
                        "company_id": line.x_company_id.id,
                        "analytic_account_id": line.x_analytic_account_id.id or False,
                        "bi_sql_model": sql_view.model_id.id,
                        "res_id": line.id,
                    }
                    vals[sql_view.view_name] = line.id
                    self.create(vals)
