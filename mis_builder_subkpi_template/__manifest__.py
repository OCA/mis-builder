# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
{
    "name": "MIS Builder Sub-KPI Template",
    "summary": "Define template to use as sub-kpi",
    "version": "11.0.1.0.0",
    "category": "Reports",
    "website": "https://www.camptocamp.com",
    "author": "Camptocamp, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "mis_builder",
    ],
    "data": [
        'security/ir.model.access.csv',
        "views/mis_report.xml",
        "views/mis_report_subkpi_template.xml",
    ],
}
