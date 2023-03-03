# Copyright 2017 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from os.path import dirname, join as opj

from odoo import fields, models, tools


class MisCommittedPurchase(models.Model):

    _name = "mis.committed.purchase"
    _description = "MIS Commitment"
    _auto = False

    line_type = fields.Char()
    name = fields.Char()
    account_id = fields.Many2one(comodel_name="account.account", string="Account")
    company_id = fields.Many2one(comodel_name="res.company", string="Company")
    credit = fields.Float()
    debit = fields.Float()
    date = fields.Date()

    # resource can be purchase.order.line or account.move.line
    res_id = fields.Integer(string="Resource ID")
    res_model = fields.Char(string="Resource Model Name")

    analytic_account_ids = fields.Many2many(
        comodel_name="account.analytic.account",
        relation="mis_committed_purchase_analytic_account_rel",
        column1="mis_committed_purchase_id",
        column2="analytic_account_id",
        string="Analytic Accounts",
    )

    def init(self):
        script = opj(
            dirname(dirname(__file__)), "examples", "mis_committed_purchase.sql"
        )

        with open(script) as f:
            tools.drop_view_if_exists(self.env.cr, "mis_committed_purchase")
            self.env.cr.execute(f.read())

            # Create many2many relation for account.analytic.account
            tools.drop_view_if_exists(
                self.env.cr, "mis_committed_purchase_analytic_account_rel"
            )
            self.env.cr.execute(
                """
            CREATE OR REPLACE VIEW mis_committed_purchase_analytic_account_rel AS
            (SELECT
                po_mcp.id AS mis_committed_purchase_id,
                jsonb_object_keys(po_rel.analytic_distribution)::INTEGER
                    AS analytic_account_id

            FROM
                purchase_order_line AS po_rel
                INNER JOIN mis_committed_purchase AS po_mcp
                    ON po_mcp.res_id = po_rel.id

            WHERE
                po_mcp.res_model = 'purchase.order.line'

            UNION ALL

            SELECT
                inv_mcp.id AS mis_committed_purchase_id,
                jsonb_object_keys(inv_rel.analytic_distribution)::INTEGER
                    AS analytic_account_id

            FROM
                account_move_line AS inv_rel
                INNER JOIN mis_committed_purchase AS inv_mcp ON
                    inv_mcp.res_id = inv_rel.id

            WHERE
                inv_mcp.res_model = 'account.move.line'
            )
            """
            )
