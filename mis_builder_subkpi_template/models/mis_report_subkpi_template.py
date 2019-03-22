# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from odoo.addons.mis_builder.models.aep import _is_domain
from odoo.tools import safe_eval


class MisReportSubkpiTemplate(models.Model):

    _name = 'mis.report.subkpi.template'
    _description = 'MIS Report Sub-KPI Template'

    name = fields.Char(required=True)
    report_ids = fields.One2many(
        'mis.report',
        'mis_report_subkpi_template_id',
    )
    subkpi_template_line_ids = fields.One2many(
        'mis.report.subkpi.template.line',
        'subkpi_template_id',
    )


class MisReportSubkpiTemplateLine(models.Model):

    _name = 'mis.report.subkpi.template.line'
    _description = 'MIS Report Sub-KPI Template Line'
    _order = 'sequence,id'

    subkpi_template_id = fields.Many2one(
        'mis.report.subkpi.template'
    )
    sequence = fields.Integer(default=1)
    name = fields.Char(size=32, required=True)
    description = fields.Char(required=True, translate=True)
    move_line_domain = fields.Char()

    @api.constrains('move_line_domain')
    def _check_move_line_domain(self):
        # TODO have a look in mis_builder for best practice in validating the
        #  domain
        if not self.move_line_domain:
            return
        ml_domain = self.move_line_domain
        if ml_domain.startswith('[') or ml_domain.endswith(']'):
            raise ValidationError(_(
                "Do not use [] inside the move line domain fields."
            ))
        if not _is_domain(ml_domain):
            raise ValidationError(_("Move line domain is not a valid domain."))
        try:
            self.env['account.move.line'].search([safe_eval(ml_domain)])
        except ValueError as e:
            raise ValidationError(_(
                "Search on Journal Items fails using this domain.")
            )
