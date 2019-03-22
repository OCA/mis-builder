# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import models, fields, api, _
from odoo.osv.expression import normalize_domain, AND
from odoo.tools import safe_eval
from odoo.exceptions import UserError
from odoo.addons.mis_builder.models.mis_report import _python_var
from odoo.addons.mis_builder.models.aep import _is_domain, \
    AccountingExpressionProcessor as AEP


class MisReport(models.Model):

    _inherit = 'mis.report'

    mis_report_subkpi_template_id = fields.Many2one(
        'mis.report.subkpi.template',
        ondelete='restrict',
    )

    @api.onchange('mis_report_subkpi_template_id')
    def onchange_mis_report_subkpi_template_id(self):
        """Fill or empty the sub-KPIs according to subkpi template"""
        if self.mis_report_subkpi_template_id:
            if self.kpi_ids.mapped('expression_ids.subkpi_id'):
                raise UserError(_(
                    "Some KPI expressions are already using sub-KPIs, "
                    "changing the sub-KPI template is therefore prohibited."
                ))
            lines = self.mis_report_subkpi_template_id.subkpi_template_line_ids
            sub_kpi_vals = []
            for line in lines:
                sub_kpi_vals.append((0, 0, {
                    'sequence': line.sequence,
                    'report_id': self.id,
                    'name': _python_var(line.name),
                    'description': line.description,
                    'subkpi_template_line_id': line.id,
                }))
            self.subkpi_ids = sub_kpi_vals
        else:
            self.subkpi_ids = None


class MisReportSubkpi(models.Model):

    _inherit = 'mis.report.subkpi'

    subkpi_template_line_id = fields.Many2one(
        'mis.report.subkpi.template.line'
    )

    def _prepare_expression(self, kpi):
        res = super()._prepare_expression(kpi)
        if not kpi.expression:
            return res
        res['base_expr'] = kpi.expression
        if not self.subkpi_template_line_id.move_line_domain:
            return res
        # AEP._ACC_RE doesn't recognize the expr if prefixed with negative
        # sign, so we handle it manually
        negative = False
        if kpi.expression.startswith('-'):
            negative = True
            base_expr = kpi.expression.lstrip('-')
        else:
            base_expr = kpi.expression
        # Match the base expr to extract move line domain
        mo = AEP._ACC_RE.match(base_expr)
        field, mode, account_sel, ml_domain = mo.groups()
        # If there's a move line domain we extend it
        if ml_domain is not None and _is_domain(ml_domain.strip('[]')):
            extended_ml_domain = str(AND([
                normalize_domain(safe_eval(ml_domain)),
                normalize_domain([
                    safe_eval(self.subkpi_template_line_id.move_line_domain)
                ])
            ]))
            new_base_expression = ''.join([field, mode, account_sel])
            # Otherwise we create a move line domain
        else:
            extended_ml_domain = "[%s]" % \
                                 self.subkpi_template_line_id.move_line_domain
            new_base_expression = base_expr
        # Restore negative sign if needed
        if negative:
            new_base_expression = "-%s" % new_base_expression
        # Build final expr with new move line domain
        res['name'] = new_base_expression + extended_ml_domain
        return res


class MisReportKpi(models.Model):

    _inherit = 'mis.report.kpi'

    base_expression = fields.Char()
    mis_report_subkpi_template_id = fields.Many2one(
        'mis.report.subkpi.template',
        related='report_id.mis_report_subkpi_template_id',
        readonly=True,
    )

    @api.multi
    def _inverse_expression(self):
        res = super()._inverse_expression()
        # TODO check if really needed as I guess the onchange takes care of it
        for kpi in self:
            kpi.base_expression = kpi.expression
        return res

    @api.onchange('multi')
    def _onchange_multi(self):
        for kpi in self:
            if not kpi.multi and kpi.expression_ids:
                kpi.expression = kpi.base_expression
            else:
                kpi.base_expression = kpi.expression
                super(MisReportKpi, kpi)._onchange_multi()
