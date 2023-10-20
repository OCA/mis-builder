# Copyright 2014 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import datetime

import odoo.tests.common as common
from odoo import fields
from odoo.tools.safe_eval import safe_eval

from ..models.accounting_none import AccountingNone
from ..models.aep import AccountingExpressionProcessor as AEP


class TestMultiCompanyAEP(common.TransactionCase):
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
        cls.res_company = cls.env["res.company"]
        cls.account_model = cls.env["account.account"]
        cls.move_model = cls.env["account.move"]
        cls.journal_model = cls.env["account.journal"]
        cls.currency_model = cls.env["res.currency"]
        cls.curr_year = datetime.date.today().year
        cls.prev_year = cls.curr_year - 1
        cls.usd = cls.currency_model.with_context(active_test=False).search(
            [("name", "=", "USD")]
        )
        cls.eur = cls.currency_model.with_context(active_test=False).search(
            [("name", "=", "EUR")]
        )
        # create company A and B
        cls.company_eur = cls.res_company.create(
            {"name": "CYEUR", "currency_id": cls.eur.id}
        )
        cls.company_usd = cls.res_company.create(
            {"name": "CYUSD", "currency_id": cls.usd.id}
        )
        cls.env["res.currency.rate"].search([]).unlink()
        type_ar = cls.env.ref("account.data_account_type_receivable")
        type_in = cls.env.ref("account.data_account_type_revenue")
        for company, divider in [(cls.company_eur, 1.0), (cls.company_usd, 2.0)]:
            # create receivable bs account
            company_key = company.name
            setattr(
                cls,
                "account_ar_" + company_key,
                cls.account_model.create(
                    {
                        "company_id": company.id,
                        "code": "400AR",
                        "name": "Receivable",
                        "user_type_id": type_ar.id,
                        "reconcile": True,
                    }
                ),
            )
            # create income pl account
            setattr(
                cls,
                "account_in_" + company_key,
                cls.account_model.create(
                    {
                        "company_id": company.id,
                        "code": "700IN",
                        "name": "Income",
                        "user_type_id": type_in.id,
                    }
                ),
            )
            # create journal
            setattr(
                cls,
                "journal" + company_key,
                cls.journal_model.create(
                    {
                        "company_id": company.id,
                        "name": "Sale journal",
                        "code": "VEN",
                        "type": "sale",
                    }
                ),
            )
            # create move in december last year
            cls._create_move(
                journal=getattr(cls, "journal" + company_key),
                date=datetime.date(cls.prev_year, 12, 1),
                amount=100 / divider,
                debit_acc=getattr(cls, "account_ar_" + company_key),
                credit_acc=getattr(cls, "account_in_" + company_key),
            )
            # create move in january this year
            cls._create_move(
                journal=getattr(cls, "journal" + company_key),
                date=datetime.date(cls.curr_year, 1, 1),
                amount=300 / divider,
                debit_acc=getattr(cls, "account_ar_" + company_key),
                credit_acc=getattr(cls, "account_in_" + company_key),
            )
            # create move in february this year
            cls._create_move(
                journal=getattr(cls, "journal" + company_key),
                date=datetime.date(cls.curr_year, 3, 1),
                amount=500 / divider,
                debit_acc=getattr(cls, "account_ar_" + company_key),
                credit_acc=getattr(cls, "account_in_" + company_key),
            )

    @classmethod
    def _create_move(cls, journal, date, amount, debit_acc, credit_acc):
        move = cls.move_model.create(
            {
                "journal_id": journal.id,
                "date": fields.Date.to_string(date),
                "line_ids": [
                    (0, 0, {"name": "/", "debit": amount, "account_id": debit_acc.id}),
                    (
                        0,
                        0,
                        {"name": "/", "credit": amount, "account_id": credit_acc.id},
                    ),
                ],
            }
        )
        move._post()
        return move

    def _do_queries(self, companies, currency, date_from, date_to):
        # create the AEP, and prepare the expressions we'll need
        aep = AEP(companies, currency)
        aep.parse_expr("bali[]")
        aep.parse_expr("bale[]")
        aep.parse_expr("balp[]")
        aep.parse_expr("balu[]")
        aep.parse_expr("bali[700IN]")
        aep.parse_expr("bale[700IN]")
        aep.parse_expr("balp[700IN]")
        aep.parse_expr("bali[400AR]")
        aep.parse_expr("bale[400AR]")
        aep.parse_expr("balp[400AR]")
        aep.parse_expr("debp[400A%]")
        aep.parse_expr("crdp[700I%]")
        aep.parse_expr("bali[400%]")
        aep.parse_expr("bale[700%]")
        aep.done_parsing()
        aep.do_queries(
            date_from=fields.Date.to_string(date_from),
            date_to=fields.Date.to_string(date_to),
        )
        return aep

    def _eval(self, aep, expr):
        eval_dict = {"AccountingNone": AccountingNone}
        return safe_eval(aep.replace_expr(expr), eval_dict)

    def _eval_by_account_id(self, aep, expr):
        res = {}
        eval_dict = {"AccountingNone": AccountingNone}
        for account_id, replaced_exprs in aep.replace_exprs_by_account_id([expr]):
            res[account_id] = safe_eval(replaced_exprs[0], eval_dict)
        return res

    def test_aep_basic(self):
        # let's query for december, one company
        aep = self._do_queries(
            self.company_eur,
            None,
            datetime.date(self.prev_year, 12, 1),
            datetime.date(self.prev_year, 12, 31),
        )
        self.assertEqual(self._eval(aep, "balp[700IN]"), -100)
        aep = self._do_queries(
            self.company_usd,
            None,
            datetime.date(self.prev_year, 12, 1),
            datetime.date(self.prev_year, 12, 31),
        )
        self.assertEqual(self._eval(aep, "balp[700IN]"), -50)
        # let's query for december, two companies
        aep = self._do_queries(
            self.company_eur | self.company_usd,
            self.eur,
            datetime.date(self.prev_year, 12, 1),
            datetime.date(self.prev_year, 12, 31),
        )
        self.assertEqual(self._eval(aep, "balp[700IN]"), -150)

    def test_aep_multi_currency(self):
        date_from = datetime.date(self.prev_year, 12, 1)
        date_to = datetime.date(self.prev_year, 12, 31)
        today = datetime.date.today()
        self.env["res.currency.rate"].create(
            dict(currency_id=self.usd.id, name=date_to, rate=1.1)
        )
        self.env["res.currency.rate"].create(
            dict(currency_id=self.usd.id, name=today, rate=1.2)
        )
        # let's query for december, one company, default currency = eur
        aep = self._do_queries(self.company_eur, None, date_from, date_to)
        self.assertEqual(self._eval(aep, "balp[700IN]"), -100)
        # let's query for december, two companies
        aep = self._do_queries(
            self.company_eur | self.company_usd, self.eur, date_from, date_to
        )
        self.assertAlmostEqual(self._eval(aep, "balp[700IN]"), -100 - 50 / 1.1)
        # let's query for december, one company, currency = usd
        aep = self._do_queries(self.company_eur, self.usd, date_from, date_to)
        self.assertAlmostEqual(self._eval(aep, "balp[700IN]"), -100 * 1.1)
        # let's query for december, two companies, currency = usd
        aep = self._do_queries(
            self.company_eur | self.company_usd, self.usd, date_from, date_to
        )
        self.assertAlmostEqual(self._eval(aep, "balp[700IN]"), -100 * 1.1 - 50)
