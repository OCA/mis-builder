# Copyright 2014 ACSONE SA/NV (<http://acsone.eu>)
# Copyright 2020 CorporateHub (https://corporatehub.eu)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import logging

from odoo import models

_logger = logging.getLogger(__name__)


class MisReportInstance(models.Model):
    _inherit = "mis.report.instance"

    def export_xls(self):
        return self.export_xlsx()

    def export_xlsx(self):
        self.ensure_one()
        return self.env.ref("mis_builder_report_xlsx.xls_export").report_action(
            self, data=dict(dummy=True)
        )  # required to propagate context
