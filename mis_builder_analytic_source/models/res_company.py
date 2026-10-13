# Copyright 2026 KMEE
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    mis_analytic_fallback_account_id = fields.Many2one(
        comodel_name="account.account",
        string="MIS Analytic Fallback Account",
        domain="[('company_id', '=', id), ('deprecated', '=', False)]",
        help="Financial account used by the MIS analytic source for analytic lines "
        "without a general account (e.g. timesheets). When empty, the company's "
        "first 'Cost of Revenue' account is used.",
    )
