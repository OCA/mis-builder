# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from odoo import models, fields, api


class MisReportInstance(models.Model):

    _inherit = 'mis.report.instance'

    report_subkpis = fields.Boolean(
        compute='_compute_report_subkpis',
        store=True,
    )
    subkpis_filter_active = fields.Boolean(
        string='Sub-KPIs filter active',
        default=False,
    )
    filter_subkpi_ids = fields.Many2many(
        'mis.report.subkpi',
        string='Sub-KPIs to display',
    )

    @api.depends('report_id', 'report_id.subkpi_ids')
    def _compute_report_subkpis(self):
        for instance in self:
            subkpis = instance.report_id.subkpi_ids
            instance.report_subkpis = bool(subkpis)

    @api.onchange('report_id')
    def _onchange_report_id(self):
        self.subkpis_filter_active = False

    @api.onchange('subkpis_filter_active')
    def _onchange_subkpis_filter_active(self):
        if self.subkpis_filter_active:
            self.filter_subkpi_ids = self.report_id.subkpi_ids
        else:
            self.filter_subkpi_ids = None

    @api.model
    def create(self, vals):
        res = super().create(vals)
        if res.subkpis_filter_active:
            res.update_columns_subkpi_filter()
        return res

    @api.multi
    def write(self, vals):
        res = super().write(vals)
        fields_to_watch = [
            'subkpis_filter_active', 'filter_subkpi_ids', 'period_ids'
        ]
        if set(vals).intersection(fields_to_watch):
            for instance in self:
                instance.update_columns_subkpi_filter()
        return res

    @api.multi
    def update_columns_subkpi_filter(self):
        self.ensure_one()
        self.period_ids.write({
            'subkpi_ids': [(6, False, self.filter_subkpi_ids.ids)]
        })


class MisReportInstancePeriod(models.Model):

    _inherit = 'mis.report.instance.period'

    subkpis_filter_active = fields.Boolean(
        related='report_instance_id.subkpis_filter_active'
    )
