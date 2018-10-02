# -*- coding: utf-8 -*-
# Copyright 2014-2018 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import logging

from odoo import api, models

_logger = logging.getLogger(__name__)


class Report(models.Model):
    _inherit = "report"

    @api.model
    def get_pdf(self, docids, report_name, html=None, data=None):
        ctx = self.env.context.copy()
        if report_name == 'mis_builder.report_mis_report_instance':
            if data.get('mis_report_remove_data'):
                # Keep filters from the URL but regenerate data
                data = None
            active_ids = self.env.context.get('active_ids')
            if not docids and active_ids:
                docids = active_ids
        if docids:
            report = self._get_report_from_name(report_name)
            obj = self.env[report.model].browse(docids)[0]
            if hasattr(obj, 'landscape_pdf') and obj.landscape_pdf:
                ctx.update({'landscape': True})
        return super(Report, self.with_context(ctx)).get_pdf(
            docids, report_name, html=html, data=data)
