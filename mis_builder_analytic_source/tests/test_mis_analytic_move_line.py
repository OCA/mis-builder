# Copyright 2026 KMEE
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import Command, fields
from odoo.tests import tagged
from odoo.tools.safe_eval import safe_eval

from odoo.addons.account.tests.common import AccountTestInvoicingCommon
from odoo.addons.mis_builder.models.accounting_none import AccountingNone
from odoo.addons.mis_builder.models.aep import AccountingExpressionProcessor as AEP


@tagged("post_install", "-at_install")
class TestMisAnalyticMoveLine(AccountTestInvoicingCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.company_data["company"]
        projects, departments = cls.env["account.analytic.plan"].create(
            [{"name": "Projects MIS"}, {"name": "Departments MIS"}]
        )
        cls.project_a, cls.project_b, cls.department = cls.env[
            "account.analytic.account"
        ].create(
            [
                {"name": "Project A", "plan_id": projects.id},
                {"name": "Project B", "plan_id": projects.id},
                {"name": "Sales department", "plan_id": departments.id},
            ]
        )
        cls.expense = cls.company_data["default_account_expense"]
        cls.date = fields.Date.from_string("2026-03-15")
        # one expense of 1000 split 60/40 between two projects, all of it on the
        # sales department (second analytic plan)
        cls.move = cls.env["account.move"].create(
            {
                "move_type": "entry",
                "journal_id": cls.company_data["default_journal_misc"].id,
                "date": cls.date,
                "line_ids": [
                    Command.create(
                        {
                            "name": "Shared cost",
                            "account_id": cls.expense.id,
                            "debit": 1000.0,
                            "analytic_distribution": {
                                f"{cls.project_a.id},{cls.department.id}": 60,
                                f"{cls.project_b.id},{cls.department.id}": 40,
                            },
                        }
                    ),
                    Command.create(
                        {
                            "name": "Shared cost",
                            "account_id": cls.company_data[
                                "default_account_payable"
                            ].id,
                            "credit": 1000.0,
                        }
                    ),
                ],
            }
        )
        cls.move.action_post()
        cls.View = cls.env["mis.analytic.move.line"]

    def _balp(self, aml_model, domain):
        aep = AEP(self.company)
        expr = f"balp[{self.expense.code}]"
        aep.parse_expr(expr)
        aep.done_parsing()
        aep.do_queries(
            date_from=self.date,
            date_to=self.date,
            additional_move_line_filter=domain,
            aml_model=aml_model,
        )
        return safe_eval(aep.replace_expr(expr), {"AccountingNone": AccountingNone})

    def _filter(self, account):
        return [("distribution_analytic_account_ids", "in", account.ids)]

    def test_lines_of_the_move(self):
        """The view has the analytic lines of the move, with debit and credit."""
        lines = self.View.search([("move_line_id.move_id", "=", self.move.id)])
        self.assertTrue(lines)
        self.assertEqual(set(lines.mapped("line_origin")), {"journal"})
        self.assertEqual(set(lines.mapped("parent_state")), {"posted"})
        self.assertEqual(lines.account_id, self.expense)
        self.assertFalse(any(lines.mapped("credit")))

    def test_analytic_filter_full_vs_prorated(self):
        """The analytic filter on journal items keeps the full balance.

        The same filter on this source gives the prorated amount, for the accounts
        of every analytic plan.
        """
        project_filter = self._filter(self.project_a)
        self.assertAlmostEqual(self._balp("account.move.line", project_filter), 1000.0)
        self.assertAlmostEqual(
            self._balp("mis.analytic.move.line", project_filter), 600.0
        )
        self.assertAlmostEqual(
            self._balp("mis.analytic.move.line", self._filter(self.project_b)), 400.0
        )
        self.assertAlmostEqual(
            self._balp("mis.analytic.move.line", self._filter(self.department)), 1000.0
        )

    def test_new_plan_rebuilds_view(self):
        """A new root plan adds a column to analytic lines: the view follows."""
        plan = self.env["account.analytic.plan"].create({"name": "Regions MIS"})
        region = self.env["account.analytic.account"].create(
            {"name": "North", "plan_id": plan.id}
        )
        manual = self.env["account.analytic.line"].create(
            {
                "name": "Regional cost",
                plan._column_name(): region.id,
                "amount": -30.0,
                "date": self.date,
                "company_id": self.company.id,
            }
        )
        line = self.View.search([("analytic_line_id", "=", manual.id)])
        self.assertAlmostEqual(line.debit, 30.0)
        self.assertEqual(line.analytic_distribution, {str(region.id): 100})
        self.assertEqual(self.View.search(self._filter(region)), line)

    def test_manual_line_fallback_account(self):
        """A line without financial account falls back to a cost account."""
        manual = self.env["account.analytic.line"].create(
            {
                "name": "Manual cost",
                "account_id": self.project_a.id,
                "amount": -50.0,
                "date": self.date,
                "company_id": self.company.id,
            }
        )
        line = self.View.search([("analytic_line_id", "=", manual.id)])
        self.assertEqual(line.line_origin, "manual")
        self.assertAlmostEqual(line.debit, 50.0)
        first_cost = self.env["account.account"].search(
            [
                ("company_ids", "in", self.company.id),
                ("account_type", "=", "expense_direct_cost"),
            ],
            order="code, id",
            limit=1,
        )
        self.assertEqual(line.account_id, first_cost)
        fallback = self.company_data["default_account_expense"]
        self.company.mis_analytic_fallback_account_id = fallback
        self.env.flush_all()
        self.View.invalidate_model()
        self.assertEqual(line.account_id, fallback)

    def test_multi_company_rule(self):
        """Users only see the lines of their companies."""
        other = self.env["res.company"].create({"name": "Other MIS company"})
        user = self.env["res.users"].create(
            {
                "name": "MIS reader",
                "login": "mis_reader_analytic",
                "company_id": other.id,
                "company_ids": [Command.set(other.ids)],
                "group_ids": [
                    Command.set(self.env.ref("account.group_account_readonly").ids)
                ],
            }
        )
        self.assertFalse(
            self.View.with_user(user).search(
                [("move_line_id.move_id", "=", self.move.id)]
            )
        )
