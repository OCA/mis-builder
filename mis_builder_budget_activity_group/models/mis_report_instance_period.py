# Copyright 2021 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class MisReportInstancePeriod(models.Model):
    _inherit = "mis.report.instance.period"

    @api.constrains("source_aml_model_id")
    def _check_source_aml_model_id(self):
        for record in self:
            # if check is_activity on mis.report, skip it.
            if not record.report_id.is_activity:
                super()._check_source_aml_model_id()
