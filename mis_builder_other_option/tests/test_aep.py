import datetime

from odoo.addons.mis_builder.models.accounting_none import AccountingNone
from odoo.addons.mis_builder.tests.test_aep import TestAEP


class TestAEPOtherOption(TestAEP):
    def setUp(self):
        super().setUp()

        # Prepare the expressions we'll need for period offset -1
        self.aep.parse_expr("bali[]" "[]" "{'period_offset': -1}")
        self.aep.parse_expr("bale[]" "[]" "{'period_offset': -1}")
        self.aep.parse_expr("balp[]" "[]" "{'period_offset': -1}")
        self.aep.parse_expr("balu[]" "[]" "{'period_offset': -1}")
        self.aep.parse_expr("bali[700IN]" "[]" "{'period_offset': -1}")
        self.aep.parse_expr("bale[700IN]" "[]" "{'period_offset': -1}")
        self.aep.parse_expr("balp[700IN]" "[]" "{'period_offset': -1}")
        self.aep.parse_expr("bali[400AR]" "[]" "{'period_offset': -1}")
        self.aep.parse_expr("bale[400AR]" "[]" "{'period_offset': -1}")
        self.aep.parse_expr("balp[400AR]" "[]" "{'period_offset': -1}")
        self.aep.parse_expr("debp[400A%]" "[]" "{'period_offset': -1}")
        self.aep.parse_expr("crdp[700I%]" "[]" "{'period_offset': -1}")
        self.aep.parse_expr("bali[400%]" "[]" "{'period_offset': -1}")
        self.aep.parse_expr("bale[700%]" "[]" "{'period_offset': -1}")
        self.aep.parse_expr(
            "balp[]" "[('account_id.code', '=', '400AR')]" "{'period_offset': -1}"
        )
        self.aep.parse_expr(
            "balp[]"
            "[('account_id.user_type_id', '=', "
            "  ref('account.data_account_type_receivable').id)]"
            "{'period_offset': -1}"
        )
        self.aep.parse_expr(
            "balp[('user_type_id', '=', "
            "      ref('account.data_account_type_receivable').id)]"
            "[]"
            "{'period_offset': -1}"
        )
        self.aep.parse_expr(
            "balp['&', "
            "     ('user_type_id', '=', "
            "      ref('account.data_account_type_receivable').id), "
            "     ('code', '=', '400AR')]"
            "[]"
            "{'period_offset': -1}"
        )

        # Prepare the expressions we'll need for period range 2
        self.aep.parse_expr("bali[]" "[]" "{'period_range': 2}")
        self.aep.parse_expr("bale[]" "[]" "{'period_range': 2}")
        self.aep.parse_expr("balp[]" "[]" "{'period_range': 2}")
        self.aep.parse_expr("balu[]" "[]" "{'period_range': 2}")
        self.aep.parse_expr("bali[700IN]" "[]" "{'period_range': 2}")
        self.aep.parse_expr("bale[700IN]" "[]" "{'period_range': 2}")
        self.aep.parse_expr("balp[700IN]" "[]" "{'period_range': 2}")
        self.aep.parse_expr("bali[400AR]" "[]" "{'period_range': 2}")
        self.aep.parse_expr("bale[400AR]" "[]" "{'period_range': 2}")
        self.aep.parse_expr("balp[400AR]" "[]" "{'period_range': 2}")
        self.aep.parse_expr("debp[400A%]" "[]" "{'period_range': 2}")
        self.aep.parse_expr("crdp[700I%]" "[]" "{'period_range': 2}")
        self.aep.parse_expr("bali[400%]" "[]" "{'period_range': 2}")
        self.aep.parse_expr("bale[700%]" "[]" "{'period_range': 2}")
        self.aep.parse_expr(
            "balp[]" "[('account_id.code', '=', '400AR')]" "{'period_range': 2}"
        )
        self.aep.parse_expr(
            "balp[]"
            "[('account_id.user_type_id', '=', "
            "  ref('account.data_account_type_receivable').id)]"
            "{'period_range': 2}"
        )
        self.aep.parse_expr(
            "balp[('user_type_id', '=', "
            "      ref('account.data_account_type_receivable').id)]"
            "[]"
            "{'period_range': 2}"
        )
        self.aep.parse_expr(
            "balp['&', "
            "     ('user_type_id', '=', "
            "      ref('account.data_account_type_receivable').id), "
            "     ('code', '=', '400AR')]"
            "[]"
            "{'period_range': 2}"
        )

    def test_aep_basic_period_offset_minus1(self):
        self.aep.done_parsing()
        # let's query for November
        self._do_queries(
            datetime.date(self.prev_year, 11, 1), datetime.date(self.prev_year, 11, 30)
        )
        # initial balance on November must be None
        self.assertIs(self._eval("bali[400AR][]{'period_offset': -1}"), AccountingNone)
        self.assertIs(self._eval("bali[700IN][]{'period_offset': -1}"), AccountingNone)
        # check variation
        self.assertEqual(self._eval("balp[400AR][]{'period_offset': -1}"), 0)
        self.assertEqual(
            self._eval(
                "balp[][('account_id.code', '=', '400AR')]{'period_offset': -1}"
            ),
            0,
        )
        self.assertEqual(
            self._eval(
                "balp[]"
                "[('account_id.user_type_id', '=', "
                "  ref('account.data_account_type_receivable').id)]"
                "{'period_offset': -1}"
            ),
            0,
        )
        self.assertEqual(
            self._eval(
                "balp[('user_type_id', '=', "
                "      ref('account.data_account_type_receivable').id)]"
                "[]"
                "{'period_offset': -1}"
            ),
            0,
        )
        self.assertEqual(
            self._eval(
                "balp['&', "
                "     ('user_type_id', '=', "
                "      ref('account.data_account_type_receivable').id), "
                "     ('code', '=', '400AR')]"
                "[]"
                "{'period_offset': -1}"
            ),
            0,
        )
        self.assertEqual(self._eval("balp[700IN][]{'period_offset': -1}"), 0)
        # check ending balance
        self.assertEqual(self._eval("bale[400AR][]{'period_offset': -1}"), 0)
        self.assertEqual(self._eval("bale[700IN][]{'period_offset': -1}"), 0)

        # let's query for December
        self._do_queries(
            datetime.date(self.prev_year, 12, 1), datetime.date(self.prev_year, 12, 31)
        )
        # initial balance on December must be None
        self.assertEqual(
            self._eval("bali[400AR][]{'period_offset': -1}"), AccountingNone
        )
        self.assertIs(self._eval("bali[700IN][]{'period_offset': -1}"), AccountingNone)
        # check variation
        self.assertEqual(self._eval("balp[400AR][]{'period_offset': -1}"), 100)
        self.assertEqual(self._eval("balp[700IN][]{'period_offset': -1}"), -100)
        # check ending balance
        self.assertEqual(self._eval("bale[400AR][]{'period_offset': -1}"), 100)
        self.assertEqual(self._eval("bale[700IN][]{'period_offset': -1}"), -100)

        # let's query for February
        self._do_queries(
            datetime.date(self.curr_year, 2, 1),
            datetime.date(self.curr_year, 2, 29 if (self.curr_year % 4 == 0) else 28),
        )
        # initial balance is the ending balance for January
        self.assertEqual(self._eval("bali[400AR][]{'period_offset': -1}"), 400)
        self.assertEqual(self._eval("bali[700IN][]{'period_offset': -1}"), -300)
        self.assertEqual(self._eval("pbali[400AR][]{'period_offset': -1}"), 400)
        self.assertEqual(self._eval("nbali[400AR][]{'period_offset': -1}"), 0)
        self.assertEqual(self._eval("nbali[700IN][]{'period_offset': -1}"), -300)
        self.assertEqual(self._eval("pbali[700IN][]{'period_offset': -1}"), 0)
        # check variation
        self.assertEqual(self._eval("balp[400AR][]{'period_offset': -1}"), 0)
        self.assertEqual(self._eval("balp[700IN][]{'period_offset': -1}"), 0)
        self.assertEqual(self._eval("nbalp[400AR][]{'period_offset': -1}"), 0)
        self.assertEqual(self._eval("pbalp[400AR][]{'period_offset': -1}"), 0)
        self.assertEqual(self._eval("nbalp[700IN][]{'period_offset': -1}"), 0)
        self.assertEqual(self._eval("pbalp[700IN][]{'period_offset': -1}"), 0)
        # check ending balance
        self.assertEqual(self._eval("bale[400AR][]{'period_offset': -1}"), 400)
        self.assertEqual(self._eval("nbale[400AR][]{'period_offset': -1}"), 0)
        self.assertEqual(self._eval("pbale[400AR][]{'period_offset': -1}"), 400)
        self.assertEqual(self._eval("bale[700IN][]{'period_offset': -1}"), -300)
        self.assertEqual(self._eval("nbale[700IN][]{'period_offset': -1}"), -300)
        self.assertEqual(self._eval("pbale[700IN][]{'period_offset': -1}"), 0)
        # check some variant expressions, for coverage
        self.assertEqual(self._eval("crdp[700I%][]{'period_offset': -1}"), 0)
        self.assertEqual(self._eval("debp[400A%][]{'period_offset': -1}"), 0)

    def test_aep_basic_period_range2(self):
        self.aep.done_parsing()
        # let's query for period range November to December
        self._do_queries(
            datetime.date(self.prev_year, 11, 1), datetime.date(self.prev_year, 12, 31)
        )
        # initial balance on November must be None
        self.assertIs(self._eval("bali[400AR][]{'period_range': 2}"), AccountingNone)
        self.assertIs(self._eval("bali[700IN][]{'period_range': 2}"), AccountingNone)
        # check variation
        self.assertEqual(self._eval("balp[400AR][]{'period_range': 2}"), 100)
        self.assertEqual(
            self._eval("balp[][('account_id.code', '=', '400AR')]{'period_range': 2}"),
            100,
        )
        self.assertEqual(
            self._eval(
                "balp[]"
                "[('account_id.user_type_id', '=', "
                "  ref('account.data_account_type_receivable').id)]"
                "{'period_range': 2}"
            ),
            100,
        )
        self.assertEqual(
            self._eval(
                "balp[('user_type_id', '=', "
                "      ref('account.data_account_type_receivable').id)]"
                "[]"
                "{'period_range': 2}"
            ),
            100,
        )
        self.assertEqual(
            self._eval(
                "balp['&', "
                "     ('user_type_id', '=', "
                "      ref('account.data_account_type_receivable').id), "
                "     ('code', '=', '400AR')]"
                "[]"
                "{'period_range': 2}"
            ),
            100,
        )
        self.assertEqual(self._eval("balp[700IN][]{'period_range': 2}"), -100)
        # check ending balance
        self.assertEqual(self._eval("bale[400AR][]{'period_range': 2}"), 100)
        self.assertEqual(self._eval("bale[700IN][]{'period_range': 2}"), -100)

        # let's query for period range December to January
        self._do_queries(
            datetime.date(self.prev_year, 12, 1), datetime.date(self.curr_year, 1, 31)
        )
        # initial balance on December must be None
        self.assertEqual(self._eval("bali[400AR][]{'period_range': 2}"), AccountingNone)
        self.assertIs(self._eval("bali[700IN][]{'period_range': 2}"), AccountingNone)
        # check variation
        self.assertEqual(self._eval("balp[400AR][]{'period_range': 2}"), 400)
        self.assertEqual(self._eval("balp[700IN][]{'period_range': 2}"), -400)
        # check ending balance
        self.assertEqual(self._eval("bale[400AR][]{'period_range': 2}"), 400)
        self.assertEqual(self._eval("bale[700IN][]{'period_range': 2}"), -400)

        # let's query for period range February to March
        self._do_queries(
            datetime.date(self.curr_year, 2, 1), datetime.date(self.curr_year, 3, 31)
        )
        # initial balance is the ending balance for January
        self.assertEqual(self._eval("bali[400AR][]{'period_range': 2}"), 400)
        self.assertEqual(self._eval("bali[700IN][]{'period_range': 2}"), -300)
        self.assertEqual(self._eval("pbali[400AR][]{'period_range': 2}"), 400)
        self.assertEqual(self._eval("nbali[400AR][]{'period_range': 2}"), 0)
        self.assertEqual(self._eval("nbali[700IN][]{'period_range': 2}"), -300)
        self.assertEqual(self._eval("pbali[700IN][]{'period_range': 2}"), 0)
        # check variation
        self.assertEqual(self._eval("balp[400AR][]{'period_range': 2}"), 500)
        self.assertEqual(self._eval("balp[700IN][]{'period_range': 2}"), -500)
        self.assertEqual(self._eval("nbalp[400AR][]{'period_range': 2}"), 0)
        self.assertEqual(self._eval("pbalp[400AR][]{'period_range': 2}"), 500)
        self.assertEqual(self._eval("nbalp[700IN][]{'period_range': 2}"), -500)
        self.assertEqual(self._eval("pbalp[700IN][]{'period_range': 2}"), 0)
        # check ending balance
        self.assertEqual(self._eval("bale[400AR][]{'period_range': 2}"), 900)
        self.assertEqual(self._eval("nbale[400AR][]{'period_range': 2}"), 0)
        self.assertEqual(self._eval("pbale[400AR][]{'period_range': 2}"), 900)
        self.assertEqual(self._eval("bale[700IN][]{'period_range': 2}"), -800)
        self.assertEqual(self._eval("nbale[700IN][]{'period_range': 2}"), -800)
        self.assertEqual(self._eval("pbale[700IN][]{'period_range': 2}"), 0)
        # check some variant expressions, for coverage
        self.assertEqual(self._eval("crdp[700I%][]{'period_range': 2}"), 500)
        self.assertEqual(self._eval("debp[400A%][]{'period_range': 2}"), 500)
