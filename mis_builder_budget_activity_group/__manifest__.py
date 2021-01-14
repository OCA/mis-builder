# Copyright 2021 Ecosoft Co., Ltd (https://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

{
    "name": "MIS Builder Budget Activity Group",
    "summary": """Select Activity Group instead of Account for MIS reports""",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "author": "Ecosoft, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/mis-builder",
    "depends": ["mis_builder_budget", "budget_activity_group"],
    "data": [
        "views/mis_report.xml",
        "views/mis_report_kpi.xml",
    ],
    "installable": True,
    "development_status": "Alpha",
    "maintainers": ["Saran440"],
}
