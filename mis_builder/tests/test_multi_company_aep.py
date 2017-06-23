# -*- coding: utf-8 -*-
# © 2014-2015 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import datetime
import time

from odoo import fields
import odoo.tests.common as common
from odoo.tools.safe_eval import safe_eval

from ..models.aep import AccountingExpressionProcessor as AEP
from ..models.accounting_none import AccountingNone


class TestMultiCompanyAEP(common.TransactionCase):

    def setUp(self):
        super(TestMultiCompanyAEP, self).setUp()
        self.res_company = self.env['res.company']
        self.account_model = self.env['account.account']
        self.move_model = self.env['account.move']
        self.journal_model = self.env['account.journal']
        self.currency_model = self.env['res.currency']
        self.curr_year = datetime.date.today().year
        self.prev_year = self.curr_year - 1
        # create company A and B
        self.companyA = self.res_company.create({
            'name': 'AEP Company A',
            'currency_id': self.currency_model.search([('code','=','USD')])})
        self.companyB = self.res_company.create({
            'name': 'AEP Company B',
            'currency_id': self.currency_model.search([('code','=','EUR')])})
        self.companies = self.res_company.browse([self.companyA.id,
                                                  self.companyB.id])
        type_ar = self.browse_ref('account.data_account_type_receivable')
        type_in = self.browse_ref('account.data_account_type_revenue')
        for company in [self.companyA, self.companyB]:
            companyKey = company.name.replace('AEP Company ','')
            if companyKey = 'A':
                divider = 1.0
            else:
                divider = 2.0
            # create receivable bs account
            setattr(self, 'account_ar_' + companyKey =\
                self.account_model.create({
                    'company_id': company.id,
                    'code': '400AR',
                    'name': 'Receivable',
                    'user_type_id': type_ar.id,
                    'reconcile': True})
            # create income pl account
            setattr(self, 'account_in_' + companyKey =\
                self.account_model.create({
                    'company_id': company.id,
                    'code': '700IN',
                    'name': 'Income',
                    'user_type_id': type_in.id})
            # create journal
            setattr(self, 'journal' + companyKey =\
                self.journal_model.create({
                    'company_id': company.id,
                    'name': 'Sale journal',
                    'code': 'VEN',
                    'type': 'sale'})
            # create move in december last year
            self._create_move(
                journal = getattr(self, 'journal' + companyKey),
                date=datetime.date(self.prev_year, 12, 1),
                amount=100/divider,
                debit_acc=getattr(self, 'account_ar_' + companyKey),
                credit_acc=getattr(self, 'account_in_' + companyKey))
            # create move in january this year
            self._create_move(
                journal = getattr(self, 'journal' + companyKey),
                date=datetime.date(self.curr_year, 1, 1),
                amount=300/divider,
                debit_acc=getattr(self, 'account_ar_' + companyKey),
                credit_acc=getattr(self, 'account_in_' + companyKey))
            # create move in february this year
            self._create_move(
                journal = getattr(self, 'journal' + companyKey),
                date=datetime.date(self.curr_year, 3, 1),
                amount=500/divider,
                debit_acc=getattr(self, 'account_ar_' + companyKey),
                credit_acc=getattr(self, 'account_in_' + companyKey))
        # create the AEP, and prepare the expressions we'll need
        
        self.aep = AEP(self.companies)
        self.aep.parse_expr("bali[]")
        self.aep.parse_expr("bale[]")
        self.aep.parse_expr("balp[]")
        self.aep.parse_expr("balu[]")
        self.aep.parse_expr("bali[700IN]")
        self.aep.parse_expr("bale[700IN]")
        self.aep.parse_expr("balp[700IN]")
        self.aep.parse_expr("bali[400AR]")
        self.aep.parse_expr("bale[400AR]")
        self.aep.parse_expr("balp[400AR]")
        self.aep.parse_expr("debp[400A%]")
        self.aep.parse_expr("crdp[700I%]")
        self.aep.parse_expr("bali[400%]")
        self.aep.parse_expr("bale[700%]")
        self.aep.parse_expr("bal_700IN")  # deprecated
        self.aep.parse_expr("bals[700IN]")  # deprecated
        self.aep.done_parsing()

    def _create_move(self, journal, date, amount, debit_acc, credit_acc):
        move = self.move_model.create({
            'journal_id': journal.id,
            'date': fields.Date.to_string(date),
            'line_ids': [(0, 0, {
                'name': '/',
                'debit': amount,
                'account_id': debit_acc.id,
            }), (0, 0, {
                'name': '/',
                'credit': amount,
                'account_id': credit_acc.id,
            })]})
        move.post()
        return move

    def _do_queries(self, date_from, date_to):
        self.aep.do_queries(
            date_from=fields.Date.to_string(date_from),
            date_to=fields.Date.to_string(date_to),
            target_move='posted')

    def _eval(self, expr):
        eval_dict = {'AccountingNone': AccountingNone}
        return safe_eval(self.aep.replace_expr(expr), eval_dict)

    def _eval_by_account_id(self, expr):
        res = {}
        eval_dict = {'AccountingNone': AccountingNone}
        for account_id, replaced_exprs in \
                self.aep.replace_exprs_by_account_id([expr]):
            res[account_id] = safe_eval(replaced_exprs[0], eval_dict)
        return res

    def test_sanity_check(self):
        self.assertEquals(self.companies.fiscalyear_last_day, 31)
        self.assertEquals(self.companies.fiscalyear_last_month, 12)

    def test_aep_basic(self):
        # let's query for december
        self._do_queries(
            datetime.date(self.prev_year, 12, 1),
            datetime.date(self.prev_year, 12, 31))
        # initial balance must be None
        self.assertIs(self._eval('bali[400AR]'), AccountingNone)
        self.assertIs(self._eval('bali[700IN]'), AccountingNone)
        # check variation
        self.assertEquals(self._eval('balp[400AR]'), 150)
        self.assertEquals(self._eval('balp[700IN]'), -150)
        # check ending balance
        self.assertEquals(self._eval('bale[400AR]'), 150)
        self.assertEquals(self._eval('bale[700IN]'), -150)

        # let's query for January
        self._do_queries(
            datetime.date(self.curr_year, 1, 1),
            datetime.date(self.curr_year, 1, 31))
        # initial balance is None for income account (it's not carried over)
        self.assertEquals(self._eval('bali[400AR]'), 150)
        self.assertIs(self._eval('bali[700IN]'), AccountingNone)
        # check variation
        self.assertEquals(self._eval('balp[400AR]'), 450)
        self.assertEquals(self._eval('balp[700IN]'), -450)
        # check ending balance
        self.assertEquals(self._eval('bale[400AR]'), 600)
        self.assertEquals(self._eval('bale[700IN]'), -450)

        # let's query for March
        self._do_queries(
            datetime.date(self.curr_year, 3, 1),
            datetime.date(self.curr_year, 3, 31))
        # initial balance is the ending balance fo January
        self.assertEquals(self._eval('bali[400AR]'), 600)
        self.assertEquals(self._eval('bali[700IN]'), -450)
        # check variation
        self.assertEquals(self._eval('balp[400AR]'), 750)
        self.assertEquals(self._eval('balp[700IN]'), -750)
        # check ending balance
        self.assertEquals(self._eval('bale[400AR]'), 1350)
        self.assertEquals(self._eval('bale[700IN]'), -1200)
        # check some variant expressions, for coverage
        self.assertEquals(self._eval('crdp[700I%]'), 750)
        self.assertEquals(self._eval('debp[400A%]'), 750)
        self.assertEquals(self._eval('bal_700IN'), -750)
        self.assertEquals(self._eval('bals[700IN]'), -1200)

        # unallocated p&l from previous year
        self.assertEquals(self._eval('balu[]'), -150)

        # TODO allocate profits, and then...
        # TODO check multi currency conversion...

    def test_aep_by_account(self):
        self._do_queries(
            datetime.date(self.curr_year, 3, 1),
            datetime.date(self.curr_year, 3, 31))
        variation = self._eval_by_account_id('balp[]')
        self.assertEquals(variation, {
            self.account_ar_A.id: 500,
            self.account_in_A.id: -500,
            self.account_ar_B.id: 250,
            self.account_in_B.id: -250,
        })
        variation = self._eval_by_account_id('balp[700IN]')
        self.assertEquals(variation, {
            self.account_in_A.id: -500,
            self.account_in_B.id: -250,
        })
        end = self._eval_by_account_id('bale[]')
        self.assertEquals(end, {
            self.account_ar_A.id: 900,
            self.account_in_A.id: -800,
            self.account_ar_B.id: 450,
            self.account_in_B.id: -400,
        })

    def test_aep_convenience_methods(self):
        initial = AEP.get_balances_initial(
            self.companies,
            time.strftime('%Y') + '-03-01',
            'posted')
        self.assertEquals(initial, {
            self.account_ar_A.id: (400, 0),
            self.account_in_A.id: (0, 300),
            self.account_ar_B.id: (200, 0),
            self.account_in_B.id: (0, 150),
        })
        variation = AEP.get_balances_variation(
            self.companies,
            time.strftime('%Y') + '-03-01',
            time.strftime('%Y') + '-03-31',
            'posted')
        self.assertEquals(variation, {
            self.account_ar_A.id: (500, 0),
            self.account_in_A.id: (0, 500),
            self.account_ar_A.id: (250, 0),
            self.account_in_B.id: (0, 250),
        })
        end = AEP.get_balances_end(
            self.companies,
            time.strftime('%Y') + '-03-31',
            'posted')
        self.assertEquals(end, {
            self.account_ar_A.id: (900, 0),
            self.account_in_A.id: (0, 800),
            self.account_ar_B.id: (450, 0),
            self.account_in_B.id: (0, 400),
        })
        unallocated = AEP.get_unallocated_pl(
            self.companies,
            time.strftime('%Y') + '-03-15',
            'posted')
        self.assertEquals(unallocated, (0, 150))

    def test_get_account_ids_for_expr(self):
        expr = 'balp[700IN]'
        account_ids = self.aep.get_account_ids_for_expr(expr)
        self.assertEquals(
            account_ids, set([self.account_in_A.id, self.account_in_B.id]))
        expr = 'balp[700%]'
        account_ids = self.aep.get_account_ids_for_expr(expr)
        self.assertEquals(
            account_ids, set([self.account_in_A.id], self.account_in_B.id))
        expr = 'bali[400%], bale[700%]'  # subkpis combined expression
        account_ids = self.aep.get_account_ids_for_expr(expr)
        self.assertEquals(
            account_ids, set([self.account_in_A.id, self.account_ar_A.id,
                              self.account_in_B.id, self.account_ar_B.id]))
