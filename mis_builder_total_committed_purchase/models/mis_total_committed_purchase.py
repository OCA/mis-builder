# Copyright 2017 ACSONE SA/NV
# Copyright 2022 Camptocamp SA (https://www.camptocamp.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models, tools
from odoo.modules.module import get_module_resource


class MisTotalCommittedPurchase(models.Model):

    _name = "mis.total.committed.purchase"
    _description = "MIS Total Purchase Commitment"
    _auto = False

    name = fields.Char()
    analytic_account_id = fields.Many2one(
        comodel_name="account.analytic.account", string="Analytic Account"
    )
    account_id = fields.Many2one(comodel_name="account.account", string="Account")
    company_id = fields.Many2one(comodel_name="res.company", string="Company")
    credit = fields.Float()
    debit = fields.Float()
    date = fields.Date()

    analytic_tag_ids = fields.Many2many(
        comodel_name="account.analytic.tag",
        relation="mis_total_committed_purchase_tag_rel",
        column1="mis_total_committed_purchase_id",
        column2="account_analytic_tag_id",
        string="Analytic Tags",
    )

    def init(self):

        with open(
            get_module_resource(
                "mis_builder_total_committed_purchase",
                "data",
                "mis_total_committed_purchase.sql",
            )
        ) as f:
            tools.drop_view_if_exists(self.env.cr, "mis_total_committed_purchase")
            self.env.cr.execute(f.read())

            with open(
                get_module_resource(
                    "mis_builder_total_committed_purchase",
                    "data",
                    "mis_total_committed_purchase_tag_rel.sql",
                )
            ) as f2:
                # Create many2many relation for account.analytic.tag
                tools.drop_view_if_exists(
                    self.env.cr, "mis_total_committed_purchase_tag_rel"
                )
                self.env.cr.execute(f2.read())
