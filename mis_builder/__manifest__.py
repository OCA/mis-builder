# Copyright 2014-2018 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "MIS Builder",
    "version": "14.0.3.6.8",
    "category": "Reporting",
    "summary": """
        Build 'Management Information System' Reports and Dashboards
    """,
    "author": "ACSONE SA/NV, " "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/mis-builder",
    "depends": [
        "account",
        "board",
        "report_xlsx",  # OCA/reporting-engine
        "date_range",  # OCA/server-ux
    ],
    "data": [
        "wizard/mis_builder_dashboard.xml",
        "views/mis_report.xml",
        "views/mis_report_instance.xml",
        "views/mis_report_style.xml",
        "datas/ir_cron.xml",
        "security/ir.model.access.csv",
        "security/mis_builder_security.xml",
        "report/mis_report_instance_qweb.xml",
        "report/mis_report_instance_xlsx.xml",
    ],
    "qweb": ["static/src/xml/mis_report_widget.xml"],
    "installable": True,
    "application": True,
    "license": "AGPL-3",
    "development_status": "Production/Stable",
    "maintainers": ["sbidoul"],
}
