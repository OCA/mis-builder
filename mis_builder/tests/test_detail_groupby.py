# Copyright 2026 Odoo Community Association (OCA)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import odoo.tests.common as common
from odoo import Command


class TestMisReportDetailGroupby(common.TransactionCase):
    """Test generic KPI expansion by a move line field."""

    def _create_move(self, date, amount, debit_acc, credit_acc, partner):
        move = self.move_model.create(
            {
                "journal_id": self.journal.id,
                "date": date,
                "partner_id": partner.id if partner else False,
                "line_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "/",
                            "debit": amount,
                            "account_id": debit_acc.id,
                            "partner_id": partner.id if partner else False,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "name": "/",
                            "credit": amount,
                            "account_id": credit_acc.id,
                            "partner_id": partner.id if partner else False,
                        },
                    ),
                ],
            }
        )
        move._post()
        return move

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env["res.company"].create({"name": "Detail Groupby Co"})
        cls.env.user.company_id = cls.company

    def setUp(self):
        super().setUp()
        self.account_model = self.env["account.account"]
        self.move_model = self.env["account.move"]
        self.journal_model = self.env["account.journal"]
        self.partner_a = self.env["res.partner"].create({"name": "Customer A"})
        self.partner_b = self.env["res.partner"].create({"name": "Customer B"})
        self.account_ar = self.account_model.create(
            {
                "company_ids": [Command.link(self.company.id)],
                "code": "400AR",
                "name": "Receivable",
                "account_type": "asset_receivable",
                "reconcile": True,
            }
        )
        self.account_in = self.account_model.create(
            {
                "company_ids": [Command.link(self.company.id)],
                "code": "700IN",
                "name": "Income",
                "account_type": "income",
            }
        )
        self.journal = self.journal_model.create(
            {
                "company_id": self.company.id,
                "name": "Sale journal",
                "code": "VEN",
                "type": "sale",
            }
        )
        self._create_move(
            "2017-01-10", 10, self.account_ar, self.account_in, self.partner_a
        )
        self._create_move(
            "2017-01-20", 7, self.account_ar, self.account_in, self.partner_b
        )
        self._create_move("2017-01-25", 3, self.account_ar, self.account_in, False)

        self.report = self.env["mis.report"].create({"name": "detail groupby report"})
        self.kpi = self.env["mis.report.kpi"].create(
            {
                "report_id": self.report.id,
                "name": "ar",
                "description": "Receivable",
                "expression": "bale[400AR]",
                "detail_groupby": "partner_id",
            }
        )
        self.instance = self.env["mis.report.instance"].create(
            {
                "name": "detail groupby instance",
                "report_id": self.report.id,
                "comparison_mode": False,
                "date_from": "2017-01-01",
                "date_to": "2017-01-31",
            }
        )

    def test_auto_expand_accounts_compat(self):
        kpi = self.env["mis.report.kpi"].create(
            {
                "report_id": self.report.id,
                "name": "legacy",
                "description": "Legacy",
                "expression": "AccountingNone",
                "auto_expand_accounts": True,
            }
        )
        self.assertEqual(kpi.detail_groupby, "account_id")
        self.assertTrue(kpi.auto_expand_accounts)

    def test_partner_detail_rows(self):
        matrix = self.instance._compute_matrix()
        rows = list(matrix.iter_rows())
        # parent KPI + 3 partner detail rows (A, B, no partner)
        self.assertEqual(len(rows), 4)
        self.assertIsNone(rows[0].detail_id)
        by_partner = {r.detail_id: r for r in rows[1:]}
        self.assertEqual(set(by_partner), {self.partner_a.id, self.partner_b.id, 0})
        for row in rows[1:]:
            self.assertEqual(row.detail_groupby, "partner_id")

        def cell_val(row):
            return next(c for c in row.iter_cells() if c).val

        self.assertEqual(cell_val(rows[0]), 20)
        self.assertEqual(cell_val(by_partner[self.partner_a.id]), 10)
        self.assertEqual(cell_val(by_partner[self.partner_b.id]), 7)
        self.assertEqual(cell_val(by_partner[0]), 3)

    def test_drilldown_partner(self):
        matrix = self.instance._compute_matrix()
        detail_row = next(
            r for r in matrix.iter_rows() if r.detail_id == self.partner_a.id
        )
        cell = next(c for c in detail_row.iter_cells() if c)
        action = self.instance.drilldown(cell.drilldown_arg)
        self.assertEqual(action["res_model"], "account.move.line")
        self.assertIn(("partner_id", "=", self.partner_a.id), action["domain"])
        self.assertEqual(cell.drilldown_arg.get("detail_groupby"), "partner_id")

    def test_journal_detail_rows(self):
        self.kpi.detail_groupby = "journal_id"
        matrix = self.instance._compute_matrix()
        rows = list(matrix.iter_rows())
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[1].detail_groupby, "journal_id")
        self.assertEqual(rows[1].detail_id, self.journal.id)
        cell = next(c for c in rows[1].iter_cells() if c)
        self.assertEqual(cell.val, 20)
