# Copyright 2016 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import odoo.tests.common as common


class TestMisReportInstance(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Remove this variable in v16 and put instead:
        # from odoo.addons.base.tests.common import DISABLED_MAIL_CONTEXT
        DISABLED_MAIL_CONTEXT = {
            "tracking_disable": True,
            "mail_create_nolog": True,
            "mail_create_nosubscribe": True,
            "mail_notrack": True,
            "no_reset_password": True,
        }
        cls.env = cls.env(context=dict(cls.env.context, **DISABLED_MAIL_CONTEXT))

    def test_supports_target_move_filter(self):
        self.assertTrue(
            self.env["mis.report"]._supports_target_move_filter("account.move.line")
        )

    def test_supports_target_move_filter_no_parent_state(self):
        self.assertFalse(
            self.env["mis.report"]._supports_target_move_filter("account.move")
        )

    def test_target_move_domain_posted(self):
        self.assertEqual(
            self.env["mis.report"]._get_target_move_domain(
                "posted", "account.move.line"
            ),
            [("parent_state", "=", "posted")],
        )

    def test_target_move_domain_all(self):
        self.assertEqual(
            self.env["mis.report"]._get_target_move_domain("all", "account.move.line"),
            [("parent_state", "in", ("posted", "draft"))],
        )

    def test_target_move_domain_no_parent_state(self):
        """Test get_target_move_domain on a model that has no parent_state."""
        self.assertEqual(
            self.env["mis.report"]._get_target_move_domain("all", "account.move"), []
        )
