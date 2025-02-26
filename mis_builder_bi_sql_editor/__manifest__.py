# Copyright 2025 - TODAY, Escodoo
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "MIS Builder BI SQL Editor",
    "summary": """
        Integrate MIS Builder to BI SQL Editor""",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "author": "Escodoo," "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/mis-builder",
    "depends": ["mis_builder", "bi_sql_editor"],
    "data": [
        "views/bi_sql_view.xml",
        "views/mis_builder_bi_sql_line.xml",
        "views/mis_report_instance.xml",
        "views/mis_report.xml",
        "security/ir.model.access.csv",
        "data/mis_builder_bi_sql_line_cron.xml",
    ],
    "installable": True,
    "application": True,
    "development_status": "Alpha",
    "maintainers": ["WesleyOliveira98"],
}
