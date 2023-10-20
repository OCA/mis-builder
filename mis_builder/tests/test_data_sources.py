# Copyright 2016 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import odoo.tests.common as common

from ..models.accounting_none import AccountingNone
from ..models.mis_report import CMP_DIFF
from ..models.mis_report_instance import (
    MODE_NONE,
    SRC_ACTUALS_ALT,
    SRC_CMPCOL,
    SRC_SUMCOL,
)
from .common import assert_matrix


class TestMisReportInstanceDataSources(common.TransactionCase):
    """Test sum and comparison data source."""

    @classmethod
    def _create_move(cls, date, amount, debit_acc, credit_acc):
        move = cls.move_model.create(
            {
                "journal_id": cls.journal.id,
                "date": date,
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
        cls.account_model = cls.env["account.account"]
        cls.move_model = cls.env["account.move"]
        cls.journal_model = cls.env["account.journal"]
        # create receivable bs account
        type_ar = cls.env.ref("account.data_account_type_receivable")
        cls.account_ar = cls.account_model.create(
            {
                "company_id": cls.env.user.company_id.id,
                "code": "400AR",
                "name": "Receivable",
                "user_type_id": type_ar.id,
                "reconcile": True,
            }
        )
        # create income account
        type_in = cls.env.ref("account.data_account_type_revenue")
        cls.account_in = cls.account_model.create(
            {
                "company_id": cls.env.user.company_id.id,
                "code": "700IN",
                "name": "Income",
                "user_type_id": type_in.id,
            }
        )
        cls.account_in2 = cls.account_model.create(
            {
                "company_id": cls.env.user.company_id.id,
                "code": "700IN2",
                "name": "Income",
                "user_type_id": type_in.id,
            }
        )
        # create journal
        cls.journal = cls.journal_model.create(
            {
                "company_id": cls.env.user.company_id.id,
                "name": "Sale journal",
                "code": "VEN",
                "type": "sale",
            }
        )
        # create move
        cls._create_move(
            date="2017-01-01",
            amount=11,
            debit_acc=cls.account_ar,
            credit_acc=cls.account_in,
        )
        # create move
        cls._create_move(
            date="2017-02-01",
            amount=13,
            debit_acc=cls.account_ar,
            credit_acc=cls.account_in,
        )
        cls._create_move(
            date="2017-02-01",
            amount=17,
            debit_acc=cls.account_ar,
            credit_acc=cls.account_in2,
        )
        # create report
        cls.report = cls.env["mis.report"].create(dict(name="test report"))
        cls.kpi1 = cls.env["mis.report.kpi"].create(
            dict(
                report_id=cls.report.id,
                name="k1",
                description="kpi 1",
                expression="-balp[700IN]",
                compare_method=CMP_DIFF,
            )
        )
        cls.expr1 = cls.kpi1.expression_ids[0]
        cls.kpi2 = cls.env["mis.report.kpi"].create(
            dict(
                report_id=cls.report.id,
                name="k2",
                description="kpi 2",
                expression="-balp[700%]",
                compare_method=CMP_DIFF,
                auto_expand_accounts=True,
            )
        )
        cls.instance = cls.env["mis.report.instance"].create(
            dict(name="test instance", report_id=cls.report.id, comparison_mode=True)
        )
        cls.p1 = cls.env["mis.report.instance.period"].create(
            dict(
                name="p1",
                report_instance_id=cls.instance.id,
                manual_date_from="2017-01-01",
                manual_date_to="2017-01-31",
            )
        )
        cls.p2 = cls.env["mis.report.instance.period"].create(
            dict(
                name="p2",
                report_instance_id=cls.instance.id,
                manual_date_from="2017-02-01",
                manual_date_to="2017-02-28",
            )
        )

    def test_sum(self):
        self.psum = self.env["mis.report.instance.period"].create(
            dict(
                name="psum",
                report_instance_id=self.instance.id,
                mode=MODE_NONE,
                source=SRC_SUMCOL,
                source_sumcol_ids=[
                    (0, 0, dict(period_to_sum_id=self.p1.id, sign="+")),
                    (0, 0, dict(period_to_sum_id=self.p2.id, sign="+")),
                ],
            )
        )
        matrix = self.instance._compute_matrix()
        # None in last col because account details are not summed by default
        assert_matrix(
            matrix,
            [
                [11, 13, 24],
                [11, 30, 41],
                [11, 13, AccountingNone],
                [AccountingNone, 17, AccountingNone],
            ],
        )

    def test_sum_diff(self):
        self.psum = self.env["mis.report.instance.period"].create(
            dict(
                name="psum",
                report_instance_id=self.instance.id,
                mode=MODE_NONE,
                source=SRC_SUMCOL,
                source_sumcol_ids=[
                    (0, 0, dict(period_to_sum_id=self.p1.id, sign="+")),
                    (0, 0, dict(period_to_sum_id=self.p2.id, sign="-")),
                ],
                source_sumcol_accdet=True,
            )
        )
        matrix = self.instance._compute_matrix()
        assert_matrix(
            matrix,
            [[11, 13, -2], [11, 30, -19], [11, 13, -2], [AccountingNone, 17, -17]],
        )

    def test_cmp(self):
        self.pcmp = self.env["mis.report.instance.period"].create(
            dict(
                name="pcmp",
                report_instance_id=self.instance.id,
                mode=MODE_NONE,
                source=SRC_CMPCOL,
                source_cmpcol_from_id=self.p1.id,
                source_cmpcol_to_id=self.p2.id,
            )
        )
        matrix = self.instance._compute_matrix()
        assert_matrix(
            matrix, [[11, 13, 2], [11, 30, 19], [11, 13, 2], [AccountingNone, 17, 17]]
        )

    def test_actuals(self):
        matrix = self.instance._compute_matrix()
        assert_matrix(matrix, [[11, 13], [11, 30], [11, 13], [AccountingNone, 17]])

    def test_actuals_disable_auto_expand_accounts(self):
        self.instance.no_auto_expand_accounts = True
        matrix = self.instance._compute_matrix()
        assert_matrix(matrix, [[11, 13], [11, 30]])

    def test_actuals_alt(self):
        aml_model = self.env["ir.model"].search([("name", "=", "account.move.line")])
        self.kpi2.auto_expand_accounts = False
        self.p1.source = SRC_ACTUALS_ALT
        self.p1.source_aml_model_id = aml_model.id
        self.p2.source = SRC_ACTUALS_ALT
        self.p1.source_aml_model_id = aml_model.id
        matrix = self.instance._compute_matrix()
        assert_matrix(matrix, [[11, 13], [11, 30]])
