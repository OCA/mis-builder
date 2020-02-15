# -*- coding: utf-8 -*-
# Copyright 2014 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import logging

from odoo import api, models

_logger = logging.getLogger(__name__)


class Report(models.Model):
    _inherit = "report"

    @api.model
    def get_pdf(self, docids, report_name, html=None, data=None):
        if report_name == "mis_builder.report_mis_report_instance":
            if not docids:
                docids = self.env.context.get("active_ids")
            mis_report_instance = self.env["mis.report.instance"].browse(docids)[0]
            context = dict(
                mis_report_instance._context_with_filters(),
                landscape=mis_report_instance.landscape_pdf,
            )
            # data=None, because it was there only to force Odoo
            # to propagate context
            return super(Report, self.with_context(context)).get_pdf(
                docids, report_name, html=html, data=None
            )
        return super(Report, self).get_pdf(docids, report_name, html=html, data=data)
