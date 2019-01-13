# Copyright 2014-2018 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import logging

from odoo import api, models

_logger = logging.getLogger(__name__)


class Report(models.Model):
    _inherit = "ir.actions.report"

    @api.multi
    def render_qweb_pdf(self, res_ids=None, data=None):
        if self.report_name == 'mis_builder.report_mis_report_instance':
            if not res_ids:
                res_ids = self.env.context.get('active_ids')
            mis_report_instance = self.env['mis.report.instance'].\
                browse(res_ids)[0]
            context = dict(
                mis_report_instance._context_with_filters(),
                landscape=mis_report_instance.landscape_pdf,
            )
            # data=None, because it was there only to force Odoo
            # to propagate context
            return super(Report, self.with_context(context)).\
                render_qweb_pdf(res_ids, data=None)
        return super(Report, self).\
            render_qweb_pdf(res_ids, data)
