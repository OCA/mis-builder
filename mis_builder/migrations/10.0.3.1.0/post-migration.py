# -*- coding: utf-8 -*-
# © 2017 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    cr = env.cr
    model = env['mis.report.instance']
    openupgrade.m2o_to_x2m(cr, model, 'mis_report_instance',
                           'company_ids', 'company_id')
