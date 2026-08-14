# Copyright 2026 Ecosoft Co., Ltd. (https://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from lxml import etree

from odoo.exceptions import AccessError, ValidationError
from odoo.tests.common import TransactionCase, new_test_user


class TestMisReportDashboard(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = new_test_user(cls.env, "mis_dashboard_user")
        cls.report = cls.env["mis.report"].create({"name": "Dashboard report"})
        cls.report_instance = cls.env["mis.report.instance"].create(
            {
                "name": "Dashboard report instance",
                "report_id": cls.report.id,
                "company_id": cls.env.company.id,
            }
        )
        cls.dashboard = cls.env.ref("board.open_board_my_dash_action")
        cls.wizard_model = cls.env[
            "add.mis.report.instance.dashboard.wizard"
        ].with_user(cls.user)
        cls.context = {
            "active_model": "mis.report.instance",
            "active_id": cls.report_instance.id,
        }

    def test_regular_user_can_add_report_to_dashboard(self):
        with self.assertRaises(AccessError):
            self.env["ir.actions.act_window"].with_user(self.user).check_access("read")

        wizard_model = self.wizard_model.with_context(**self.context)
        defaults = wizard_model.default_get(["name", "dashboard_id"])
        self.assertEqual(defaults["dashboard_id"], self.dashboard.id)
        selections = (
            self.env["ir.actions.act_window"]
            .with_user(self.user)
            .with_context(mis_builder_dashboard_selection=True)
            .name_search(args=[("res_model", "=", "board.board")])
        )
        self.assertIn((self.dashboard.id, self.dashboard.display_name), selections)
        wizard = wizard_model.create(defaults)
        values = wizard.web_read({"dashboard_id": {"fields": {"display_name": {}}}})
        self.assertEqual(values[0]["dashboard_id"]["id"], self.dashboard.id)

        self.assertEqual(
            wizard.action_add_to_dashboard(), {"type": "ir.actions.act_window_close"}
        )
        customization = (
            self.env["ir.ui.view.custom"]
            .sudo()
            .search(
                [
                    ("user_id", "=", self.user.id),
                    ("ref_id", "=", self.dashboard.view_id.id),
                ],
                limit=1,
            )
        )
        self.assertTrue(customization)
        action_nodes = etree.fromstring(customization.arch).xpath("//action")
        self.assertEqual(action_nodes[-1].get("string"), self.report_instance.name)

    def test_regular_user_cannot_use_restricted_dashboard_action(self):
        restricted_dashboard = self.env["ir.actions.act_window"].create(
            {
                "name": "Restricted dashboard",
                "res_model": "board.board",
                "view_mode": "form",
                "view_id": self.dashboard.view_id.id,
                "groups_id": [(6, 0, [self.env.ref("base.group_system").id])],
            }
        )
        wizard = self.env["add.mis.report.instance.dashboard.wizard"].create(
            {
                "name": self.report_instance.name,
                "dashboard_id": restricted_dashboard.id,
            }
        )

        with self.assertRaises(ValidationError):
            wizard.with_user(self.user).with_context(
                **self.context
            ).action_add_to_dashboard()
