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
    def setUpClass(cls, chart_template_ref=None):
        super().setUpClass(chart_template_ref=chart_template_ref)
        cls.company = cls.company_data["company"]
        plan = cls.env["account.analytic.plan"].create({"name": "Projects"})
        cls.project_a, cls.project_b = cls.env["account.analytic.account"].create(
            [
                {"name": "Project A", "plan_id": plan.id, "company_id": cls.company.id},
                {"name": "Project B", "plan_id": plan.id, "company_id": cls.company.id},
            ]
        )
        cls.expense = cls.company_data["default_account_expense"]
        cls.date = fields.Date.from_string("2026-03-15")
        # one expense of 1000 split 60/40 between the two projects
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
                                str(cls.project_a.id): 60,
                                str(cls.project_b.id): 40,
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
        aep.parse_expr(f"balp[{self.expense.code}]")
        aep.done_parsing()
        aep.do_queries(
            date_from=self.date,
            date_to=self.date,
            additional_move_line_filter=domain,
            aml_model=aml_model,
        )
        return safe_eval(
            aep.replace_expr(f"balp[{self.expense.code}]"),
            {"AccountingNone": AccountingNone},
        )

    def test_prorated_lines(self):
        """One view line per analytic account, with the distributed amount."""
        lines = self.View.search([("move_line_id.move_id", "=", self.move.id)])
        by_project = {line.analytic_account_id: line for line in lines}
        self.assertEqual(set(by_project), {self.project_a, self.project_b})
        line_a = by_project[self.project_a]
        self.assertEqual(line_a.account_id, self.expense)
        self.assertEqual(line_a.line_origin, "journal")
        self.assertEqual(line_a.parent_state, "posted")
        self.assertAlmostEqual(line_a.debit, 600.0)
        self.assertAlmostEqual(line_a.credit, 0.0)
        self.assertAlmostEqual(line_a.balance, 600.0)
        self.assertAlmostEqual(by_project[self.project_b].balance, 400.0)

    def test_analytic_filter_full_vs_prorated(self):
        """The MIS analytic filter on journal items keeps the full balance.

        The same filter on this source gives the prorated amount, without changing
        the domain written by mis_builder.
        """
        domain = [("analytic_distribution_search", "in", [self.project_a.id])]
        self.assertAlmostEqual(self._balp("account.move.line", domain), 1000.0)
        self.assertAlmostEqual(self._balp("mis.analytic.move.line", domain), 600.0)
        domain_b = [("analytic_account_id", "=", self.project_b.id)]
        self.assertAlmostEqual(self._balp("mis.analytic.move.line", domain_b), 400.0)

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
                ("company_id", "=", self.company.id),
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
        other = self.company_data_2["company"]
        user = self.env["res.users"].create(
            {
                "name": "MIS reader",
                "login": "mis_reader_analytic",
                "company_id": other.id,
                "company_ids": [Command.set(other.ids)],
                "groups_id": [
                    Command.set(self.env.ref("account.group_account_readonly").ids)
                ],
            }
        )
        self.assertFalse(
            self.View.with_user(user).search(
                [("move_line_id.move_id", "=", self.move.id)]
            )
        )
