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
    analytic_account_id = fields.Many2one(
        comodel_name="account.analytic.account", string="Analytic Account"
    )
    account_id = fields.Many2one(comodel_name="account.account", string="Account")
    company_id = fields.Many2one(comodel_name="res.company", string="Company")
    credit = fields.Float()
    debit = fields.Float()
    date = fields.Date()

    # resource can be purchase.order.line or account.move.line
    res_id = fields.Integer(string="Resource ID")
    res_model = fields.Char(string="Resource Model Name")

    analytic_tag_ids = fields.Many2many(
        comodel_name="account.analytic.tag",
        relation="mis_committed_purchase_tag_rel",
        column1="mis_committed_purchase_id",
        column2="account_analytic_tag_id",
        string="Analytic Tags",
    )

    def init(self):
        script = opj(
            dirname(dirname(__file__)), "examples", "mis_committed_purchase.sql"
        )
        with open(script) as f:
            tools.drop_view_if_exists(self.env.cr, "mis_committed_purchase")
            self.env.cr.execute(f.read())

            # Create many2many relation for account.analytic.tag
            tools.drop_view_if_exists(self.env.cr, "mis_committed_purchase_tag_rel")
            self.env.cr.execute(
                """
            CREATE OR REPLACE VIEW mis_committed_purchase_tag_rel AS
            (SELECT
                po_mcp.id AS mis_committed_purchase_id,
                po_rel.account_analytic_tag_id AS account_analytic_tag_id
            FROM account_analytic_tag_purchase_order_line_rel AS po_rel
            INNER JOIN mis_committed_purchase AS po_mcp ON
                po_mcp.res_id = po_rel.purchase_order_line_id
            WHERE po_mcp.res_model = 'purchase.order.line'
            UNION ALL
            SELECT
                inv_mcp.id AS mis_committed_purchase_id,
                inv_rel.account_analytic_tag_id AS account_analytic_tag_id
            FROM account_analytic_tag_account_move_line_rel AS inv_rel
            INNER JOIN mis_committed_purchase AS inv_mcp ON
                inv_mcp.res_id = inv_rel.account_move_line_id
            WHERE inv_mcp.res_model = 'account.move.line')
            """
            )
