# Copyright 2014-2018 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import logging

from odoo import api, models

_logger = logging.getLogger(__name__)


class Report(models.Model):
    _inherit = "ir.actions.report"

    @api.multi
    def render_qweb_pdf(self, res_ids=None, data=None):
        ctx = self.env.context.copy()
        if res_ids:
            obj = self.env[self.model].browse(res_ids)[0]
            if hasattr(obj, 'landscape_pdf') and obj.landscape_pdf:
                ctx.update({'landscape': True})
        return super(Report, self.with_context(ctx)).render_qweb_pdf(
            res_ids, data
        )
