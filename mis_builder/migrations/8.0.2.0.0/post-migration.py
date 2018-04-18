# -*- coding: utf-8 -*-
# Copyright 2017-2018 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openerp import api, SUPERUSER_ID


def fill_defaults(env):
    cr = env.cr

    default_specs = {
        'mis.report.instance.period': ['report_instance_id'],
        'mis.report.kpi': ['report_id'],
        'mis.report.query': ['report_id'],
        'mis.report.instance': ['company_id'],
    }

    for model in default_specs.keys():
        obj = env[model]
        for field in default_specs[model]:
            value = obj.default_get([field])
            if value:
                cr.execute("UPDATE %s SET %s = %s WHERE %s is NULL" % (
                    obj._table, field, value, field))


def migrate(cr, version):
    cr.execute("""
        INSERT INTO mis_report_kpi_expression
            (create_uid, create_date, write_uid, write_date,
             kpi_id, name, sequence)
        SELECT create_uid, create_date, write_uid, write_date,
               id, old_expression, sequence
        FROM mis_report_kpi
    """)
    cr.execute("""
        ALTER TABLE mis_report_kpi
        DROP COLUMN old_expression
    """)
    # set default mode to relative for existing periods
    # as it was the only mode in previous versions
    cr.execute("""
        UPDATE mis_report_instance_period
        SET mode='relative'
    """)
    # set defaults in now required fields
    env = api.Environment(cr, SUPERUSER_ID, {})
    fill_defaults(env)
