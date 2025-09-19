# Copyright 2017-2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "MIS Builder - Report XLSX",
    "summary": "Export MIS Reports in XLSX format",
    "version": "18.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV, GRAP, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/mis-builder",
    "depends": ["mis_builder", "report_xlsx"],
    "data": [
        "report/mis_report_instance_xlsx.xml",
        "views/mis_report_instance.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "mis_builder_report_xlsx/static/src/*/**.js",
            "mis_builder_report_xlsx/static/src/*/**.xml",
        ]
    },
    "installable": True,
    "auto_install": True,
    "maintainers": ["sbidoul"],
}
