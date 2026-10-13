# Copyright 2026 KMEE
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "MIS Builder Analytic Source",
    "summary": "Analytic lines as the move lines source of MIS reports, so "
    "analytic filters give the prorated amounts",
    "version": "18.0.1.0.0",
    "development_status": "Alpha",
    "category": "Reporting",
    "author": "KMEE, Odoo Community Association (OCA)",
    "maintainers": ["mileo"],
    "website": "https://github.com/OCA/mis-builder",
    "license": "AGPL-3",
    "depends": ["mis_builder", "account"],
    "data": [
        "security/ir.model.access.csv",
        "security/ir_rule.xml",
        "views/mis_analytic_move_line_views.xml",
        "views/res_config_settings_views.xml",
    ],
    "installable": True,
}
