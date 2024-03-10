# Copyright 2014 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import odoo.tests.common as common

from ..models.mis_report import _utc_midnight


class TestUtcMidnight(common.TransactionCase):
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

    def test_utc_midnight(self):
        date_to_convert = "2014-07-05"
        date_time_convert = _utc_midnight(date_to_convert, "Europe/Brussels")
        self.assertEqual(date_time_convert, "2014-07-04 22:00:00")
        date_time_convert = _utc_midnight(date_to_convert, "Europe/Brussels", add_day=1)
        self.assertEqual(date_time_convert, "2014-07-05 22:00:00")
        date_time_convert = _utc_midnight(date_to_convert, "US/Pacific")
        self.assertEqual(date_time_convert, "2014-07-05 07:00:00")
        date_time_convert = _utc_midnight(date_to_convert, "US/Pacific", add_day=1)
        self.assertEqual(date_time_convert, "2014-07-06 07:00:00")
