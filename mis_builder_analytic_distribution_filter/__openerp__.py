# -*- coding: utf-8 -*-
# Copyright 2016 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': "MIS Builder Analytic Distribution Filter",
    'version': '8.0.1.0.0',
    'category': 'Reporting',
    'summary': """
        Add analytic distribution filter to MIS Reports
    """,
    'author': 'Sunflower IT'
              'Odoo Community Association (OCA)',
    'website': "http://sunflowerweb.nl",
    'license': 'AGPL-3',
    'depends': [
        'mis_builder_analytic_filter',
        'account_analytic_plans',
    ],
    'data': [
        'views/mis_report_view.xml',
        'views/mis_builder_analytic.xml',
    ],
    'qweb': [
        'static/src/xml/mis_widget.xml'
    ],
}
