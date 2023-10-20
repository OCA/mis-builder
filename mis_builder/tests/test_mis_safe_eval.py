# Copyright 2016 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import odoo.tests.common as common

from ..models.mis_safe_eval import DataError, NameDataError, mis_safe_eval


class TestMisSafeEval(common.TransactionCase):
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

    def test_nominal(self):
        val = mis_safe_eval("a + 1", {"a": 1})
        self.assertEqual(val, 2)

    def test_exceptions(self):
        val = mis_safe_eval("1/0", {})  # division by zero
        self.assertTrue(isinstance(val, DataError))
        self.assertEqual(val.name, "#DIV/0")
        val = mis_safe_eval("1a", {})  # syntax error
        self.assertTrue(isinstance(val, DataError))
        self.assertEqual(val.name, "#ERR")

    def test_name_error(self):
        val = mis_safe_eval("a + 1", {})
        self.assertTrue(isinstance(val, NameDataError))
        self.assertEqual(val.name, "#NAME")
