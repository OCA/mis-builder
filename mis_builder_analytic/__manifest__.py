# Copyright 2018 Tecnativa - Ernesto Tejeda
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    'name': 'MIS Builder Analytic',
    'summary': "Provide account analytic lines for MIS builder reports",
    'version': '11.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'Tecnativa, '
              'Odoo Community Association (OCA)',
    'website': 'https://github.com/OCA/mis-builder',
    'depends': [
        'mis_builder',
    ],
    'data': [
        'views/mis_account_analytic_line_views.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
}
