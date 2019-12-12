# -*- coding: utf-8 -*-
# Copyright 2016 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "MIS Builder NonZero Accounts",
    "version": "10.0.1.0.0",
    "category": "Reporting",
    "summary": """
        Ads a boolean on mis reports to filter out KPI with zero balance
    """,
    "author": "Decodio d.o.o., "
              "Odoo Community Association (OCA)"
    ,
    "website": "https://decod.io",
    "license": "AGPL-3",
    "depends": ["mis_builder",],
    "data": ["views/mis_report_view.xml",],
}
