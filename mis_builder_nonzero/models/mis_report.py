# -*- coding: utf-8 -*-
# Copyright 2016 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class MisReportInstance(models.Model):
    _inherit = 'mis.report.instance'

    account_nonzero = fields.Boolean(
        string='Only with values', default=True,
        help="If checked only KPI lines with values are listed in report"
    )

    @api.multi
    def compute(self):
        res = super(MisReportInstance, self).compute()
        if self.account_nonzero:
            content = []
            for line in res['content']:
                for col in line['cols']:
                    if col['val'] != 0.0 and col['val'] is not None:
                        if line not in content:
                            content.append(line)
            res['content'] = content
        return res
