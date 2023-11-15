# Copyright 2017 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from os.path import dirname
from os.path import join as opj

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

    def init(self):
        script = opj(
            dirname(dirname(__file__)), "examples", "mis_committed_purchase.sql"
        )
        with open(script) as f:
            tools.drop_view_if_exists(self.env.cr, "mis_committed_purchase")
            self.env.cr.execute(f.read())
