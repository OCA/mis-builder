# Copyright 2026 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
import datetime

from odoo import fields
from odoo.tests import common


class TestMisReportAccountCoverageCheck(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # use a dedicated company so the test is not affected by any chart
        # of accounts / demo postings that other installed modules may have
        # set up on the default company
        cls.company = cls.env["res.company"].create({"name": "Coverage Check Co"})
        type_ar = cls.env.ref("account.data_account_type_receivable")
        type_in = cls.env.ref("account.data_account_type_revenue")
        type_asset = cls.env.ref("account.data_account_type_current_assets")
        cls.account_ar = cls.env["account.account"].create(
            {
                "company_id": cls.company.id,
                "code": "400AR",
                "name": "Receivable",
                "user_type_id": type_ar.id,
                "reconcile": True,
            }
        )
        cls.account_uncovered = cls.env["account.account"].create(
            {
                "company_id": cls.company.id,
                "code": "500UN",
                "name": "Uncovered account",
                "user_type_id": type_in.id,
            }
        )
        cls.account_in = cls.env["account.account"].create(
            {
                "company_id": cls.company.id,
                "code": "700IN",
                "name": "Income",
                "user_type_id": type_in.id,
            }
        )
        cls.account_out_of_range = cls.env["account.account"].create(
            {
                "company_id": cls.company.id,
                "code": "900OU",
                "name": "Out of range account",
                "user_type_id": type_in.id,
            }
        )
        # balance-sheet account (no posting yet): used to check that, with
        # no closing/opening entries, its balance keeps accumulating from
        # before the period being checked
        cls.account_bs_old = cls.env["account.account"].create(
            {
                "company_id": cls.company.id,
                "code": "450OL",
                "name": "Old balance-sheet account",
                "user_type_id": type_asset.id,
            }
        )
        # P&L account (no posting yet): used to check that, unlike balance
        # -sheet accounts, its balance resets every fiscal year
        cls.account_pl_old = cls.env["account.account"].create(
            {
                "company_id": cls.company.id,
                "code": "480PL",
                "name": "Old P&L account",
                "user_type_id": type_in.id,
            }
        )
        cls.journal = cls.env["account.journal"].create(
            {
                "company_id": cls.company.id,
                "name": "Sale journal",
                "code": "VEN",
                "type": "sale",
            }
        )
        cls.date_from = datetime.date.today().replace(day=1)
        next_month = cls.date_from.replace(day=28) + datetime.timedelta(days=4)
        cls.date_to = next_month - datetime.timedelta(days=next_month.day)
        # covered postings: only account_ar/account_in appear in the KPI expr
        cls._create_move(cls.account_ar, cls.account_in, 100)
        # uncovered-but-used posting, in range: must be detected
        cls._create_move(cls.account_ar, cls.account_uncovered, 50)
        # posting on an out-of-range account: must never be detected
        cls._create_move(cls.account_ar, cls.account_out_of_range, 20)

        cls.report = cls.env["mis.report"].create({"name": "Test report"})
        cls.env["mis.report.kpi"].create(
            {
                "report_id": cls.report.id,
                "name": "balance",
                "description": "Balance",
                "expression_ids": [(0, 0, {"name": "balp[400AR,700IN]"})],
            }
        )
        cls.instance = cls.env["mis.report.instance"].create(
            {
                "name": "Test instance",
                "report_id": cls.report.id,
                "company_id": cls.company.id,
                "date_from": fields.Date.to_string(cls.date_from),
                "date_to": fields.Date.to_string(cls.date_to),
                "period_ids": [(0, 0, {"name": "Default"})],
            }
        )

    @classmethod
    def _create_move(cls, debit_account, credit_account, amount, date=None):
        move = cls.env["account.move"].create(
            {
                "journal_id": cls.journal.id,
                "date": fields.Date.to_string(date or cls.date_from),
                "line_ids": [
                    (
                        0,
                        0,
                        {"name": "/", "debit": amount, "account_id": debit_account.id},
                    ),
                    (
                        0,
                        0,
                        {
                            "name": "/",
                            "credit": amount,
                            "account_id": credit_account.id,
                        },
                    ),
                ],
            }
        )
        move._post()
        return move

    def _create_wizard(self):
        return self.env["mis.report.account.coverage.check"].create(
            {
                "report_instance_id": self.instance.id,
                "account_code_from": "400AR",
                "account_code_to": "700IN",
            }
        )

    def test_uncovered_account_detected(self):
        wizard = self._create_wizard()
        wizard.action_check()
        self.assertEqual(wizard.state, "done")
        self.assertEqual(len(wizard.line_ids), 1)
        line = wizard.line_ids
        self.assertEqual(line.account_id, self.account_uncovered)
        self.assertEqual(line.debit, 0)
        self.assertEqual(line.credit, 50)
        self.assertEqual(line.balance, -50)

    def test_old_posting_on_balance_sheet_account_detected(self):
        # without closing/opening entries, a balance-sheet account's balance
        # keeps accumulating: a posting from a year before the period being
        # checked must still surface the account as uncovered
        old_date = self.date_from.replace(year=self.date_from.year - 1)
        self._create_move(self.account_bs_old, self.account_ar, 40, date=old_date)
        wizard = self._create_wizard()
        wizard.action_check()
        result_accounts = wizard.line_ids.mapped("account_id")
        self.assertIn(self.account_bs_old, result_accounts)
        line = wizard.line_ids.filtered(
            lambda line_: line_.account_id == self.account_bs_old
        )
        self.assertEqual(line.debit, 40)
        self.assertEqual(line.balance, 40)

    def test_old_posting_on_pl_account_not_detected(self):
        # unlike balance-sheet accounts, P&L accounts reset every fiscal
        # year: a posting from the previous fiscal year must NOT make the
        # account show up when checking the current period
        old_date = self.date_from.replace(year=self.date_from.year - 1)
        self._create_move(self.account_ar, self.account_pl_old, 40, date=old_date)
        wizard = self._create_wizard()
        wizard.action_check()
        self.assertNotIn(self.account_pl_old, wizard.line_ids.mapped("account_id"))

    def test_covered_accounts_not_listed(self):
        wizard = self._create_wizard()
        wizard.action_check()
        result_accounts = wizard.line_ids.mapped("account_id")
        self.assertNotIn(self.account_ar, result_accounts)
        self.assertNotIn(self.account_in, result_accounts)

    def test_out_of_range_account_not_listed(self):
        wizard = self._create_wizard()
        wizard.action_check()
        self.assertNotIn(
            self.account_out_of_range, wizard.line_ids.mapped("account_id")
        )

    def test_view_move_lines_action_domain(self):
        wizard = self._create_wizard()
        wizard.action_check()
        line = wizard.line_ids
        action = line.action_view_move_lines()
        move_lines = self.env[action["res_model"]].search(action["domain"])
        self.assertTrue(move_lines)
        self.assertEqual(
            set(move_lines.mapped("account_id.id")), {self.account_uncovered.id}
        )

    def test_action_back_resets_state(self):
        wizard = self._create_wizard()
        wizard.action_check()
        wizard.action_back()
        self.assertEqual(wizard.state, "init")
        self.assertFalse(wizard.line_ids)
