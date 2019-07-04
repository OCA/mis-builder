# Copyright 2019 Martronic SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'MIS Builder Demo',
    'summary': """
        Demo addon for MIS Builder""",
    'version': '11.0.3.0.1',
    'license': 'AGPL-3',
    'author': 'Martronic SA, '
              'ACSONE SA/NV, '
              'Odoo Community Association (OCA)',
    'website': 'https://github.com/OCA/mis-builder',
    'depends': [
        'mis_builder'
    ],
    'data': [
        'data/styles.xml',
        'data/reports.xml',
        'data/kpis.xml',
        'data/instances.xml',
        'data/menus.xml',
    ],
    'installable': True,
    'maintainers': ['Martronic-SA','sbidoul'],
    'development_status': 'Beta',
}
