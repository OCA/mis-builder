# Copyright 2019-2020 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import models


class MisBudget(models.Model):
    _name = "mis.budget"
    _inherit = ["mis.budget", "tier.validation"]
    _state_from = ["draft"]
    _state_to = ["confirmed"]

