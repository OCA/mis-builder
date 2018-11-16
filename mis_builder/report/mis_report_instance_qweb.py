# -*- coding: utf-8 -*-
# Copyright 2014-2018 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import logging

from openerp import api, models

_logger = logging.getLogger(__name__)


class Report(models.Model):
    _inherit = "report"

    @api.v7
    def get_pdf(self, cr, uid, ids, report_name, html=None, data=None,
                context=None):
        if report_name == 'mis_builder.report_mis_report_instance':
            if not ids:
                ids = context.get('active_ids')
            mis_report_instance = self.pool['mis.report.instance'].browse(
                cr, uid, ids, context=context)[0]
            context = dict(
                mis_report_instance._context_with_filters(),
                landscape=mis_report_instance.landscape_pdf,
            )
            # data=None, because it was there only to force Odoo
            # to propagate context
            return super(Report, self).get_pdf(cr, uid, ids, report_name,
                                               html=html, data=None,
                                               context=context)
        return super(Report, self).get_pdf(cr, uid, ids, report_name,
                                           html=html, data=data,
                                           context=context)

    @api.v8
    def get_pdf(self, records, report_name, html=None, data=None):
        return self._model.get_pdf(self._cr, self._uid,
                                   records.ids, report_name,
                                   html=html, data=data, context=self._context)
