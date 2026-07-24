# Copyright 2026 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    "name": "MIS Report Account Coverage Check",
    "version": "15.0.1.0.0",
    "category": "Accounting",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/mis-builder",
    "license": "AGPL-3",
    "depends": ["account", "mis_builder"],
    "data": [
        "security/ir.model.access.csv",
        "wizard/mis_report_account_coverage_check_views.xml",
        "views/mis_report_instance_views.xml",
    ],
    "installable": True,
    "maintainers": ["carlosdauden"],
}
