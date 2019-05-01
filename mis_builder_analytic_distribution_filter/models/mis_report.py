# -*- coding: utf-8 -*-
# Copyright 2016 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, fields, models


class MisReportInstance(models.Model):
    _inherit = 'mis.report.instance'

    analytic_distribution_id = fields.Many2one(
        comodel_name='account.analytic.plan.instance',
        string='Analytic Distribution')

    @api.multi
    def preview(self):
        self.ensure_one()
        res = super(MisReportInstance, self).preview()
        res['context'] = {
            'analytic_distribution_id': self.analytic_distribution_id.id,
        }
        return res


class MisReportInstancePeriod(models.Model):
    _inherit = 'mis.report.instance.period'

    @api.multi
    def _get_additional_move_line_filter(self):
        self.ensure_one()
        res = super(MisReportInstancePeriod, self).\
            _get_additional_move_line_filter()
        val = self.env.context.get('analytic_distribution_id')
        if val:
            res.append(('analytics_id', '=', val))
        return res
