# Copyright 2026 KMEE
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    mis_analytic_fallback_account_id = fields.Many2one(
        related="company_id.mis_analytic_fallback_account_id",
        readonly=False,
    )
