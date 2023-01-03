# Copyright 2023 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models

class MisReportInstance(models.Model):

    _inherit = "mis.report.instance"

    company_ids = fields.Many2many(
        "res.company",
        string="Companies",
    )


class MisReportInstancePeriod(models.Model):

    _inherit = "mis.report.instance.period"

    company_ids = fields.Many2many(
        "res.company",
        string="Companies",
    )

    def _get_additional_move_line_filter(self):
        aml_domain = super(
            MisReportInstancePeriod, self
        )._get_additional_move_line_filter()
        sudoself = self.sudo()
        if sudoself.report_instance_id.company_ids:
            aml_domain.append(
                (
                    "company_id",
                    "in",
                    sudoself.report_instance_id.company_ids.ids,
                )
            )
        if sudoself.company_ids:
            aml_domain.append(
                ("company_id", "in", sudoself.company_ids.ids)
            )
        return aml_domain
