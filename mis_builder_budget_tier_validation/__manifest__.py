# Copyright 2019-2020 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Mis Builder Budget Tier Validation",
    "summary": "Extends the functionality of Mis Builder Budget to "
    "support a tier validation process.",
    "version": "13.0.1.0.0",
    "website": "https://github.com/OCA/mis-builder/",
    "author": "QubiQ 2010, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": ["mis_builder_budget", "base_tier_validation"],
    "data": [
        "views/mis_budget_view.xml",
    ],
}
