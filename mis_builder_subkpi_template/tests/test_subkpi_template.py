# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo.tests import SavepointCase
from odoo.tools import safe_eval
from odoo.addons.mis_builder.models.aep \
    import AccountingExpressionProcessor as AEP


class TestSubkpiTemplate(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        used_partners = cls.env['account.move.line'].search([]).mapped(
            'partner_id'
        )
        template_line_vals = []
        for partner in used_partners:
            template_line_vals.append((0, 0, {
                'name': partner.name,
                'description': partner.name,
                'move_line_domain': "('partner_id', '=', %s)" % partner.id,
            }))
        cls.subkpi_template = cls.env['mis.report.subkpi.template'].create({
            'name': 'Partners subkpis',
            'subkpi_template_line_ids': template_line_vals,
        })

    def assert_multi_kpi_subkpi(self, kpi):
        self.assertEqual(
            # FIXME somehow we still have a kpi expression not linked to a
            #  sub KPI
            len(kpi.expression_ids.filtered(
                lambda e: e.subkpi_id
            )),
            len(self.subkpi_template.subkpi_template_line_ids)
        )
        for expr in kpi.expression_ids:
            # FIXME somehow we still have a kpi expression not linked to a
            #  sub KPI
            if not expr.subkpi_id:
                continue
            # Match the expr to extract move line domain
            mo = AEP._ACC_RE.match(expr.name)
            field, mode, account_sel, ml_domain = mo.groups()
            # TODO Improve using osv.expression ?
            self.assertIn(
                expr.subkpi_id.subkpi_template_line_id.move_line_domain,
                ml_domain
            )
            # Test searching move lines with the domain to ensure there is only
            # one partner
            move_lines = self.env['account.move.line'].search(
                safe_eval(ml_domain)
            )
            if move_lines:
                self.assertEqual(len(move_lines.mapped('partner_id')), 1)

    def test_subkpi_template(self):
        test_report = self.env['mis.report'].create({
            'name': 'Test report',
            'mis_report_subkpi_template_id': self.subkpi_template.id,
        })
        test_report.onchange_mis_report_subkpi_template_id()
        kpi_receivable = self.env['mis.report.kpi'].create({
            'report_id': test_report.id,
            'description': 'receivable',
            'name': 'receivable',
            'expression': "balp[1012%]",
        })
        kpi_receivable.multi = True
        kpi_receivable._onchange_multi()
        self.assert_multi_kpi_subkpi(kpi_receivable)
        kpi_income = self.env['mis.report.kpi'].create({
            'report_id': test_report.id,
            'description': 'income',
            'name': 'income',
            'expression': "balp[20%][('blocked', '=', False)]",
        })
        kpi_income.multi = True
        kpi_income._onchange_multi()
        self.assert_multi_kpi_subkpi(kpi_income)
        kpi_total = self.env['mis.report.kpi'].create({
            'report_id': test_report.id,
            'description': 'total',
            'name': 'total',
            'expression': "sales + income",
        })
        # No added domain when multi is off
        self.assertEqual(len(kpi_total.expression_ids), 1)
        self.assertEqual(kpi_total.expression_ids.name, "sales + income")
