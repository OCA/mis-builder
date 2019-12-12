# -*- coding: utf-8 -*-
# Copyright 2016-2018 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import contextlib
import shutil
import tempfile

import odoo.tests.common as common
from odoo import tools
from odoo.tools import test_reports

from ..models.accounting_none import AccountingNone
from ..models.mis_report import TYPE_STR, SubKPITupleLengthError, SubKPIUnknownTypeError


@contextlib.contextmanager
def enable_test_report_directory():
    tmpdir = tempfile.mkdtemp()
    prev_test_report_dir = tools.config["test_report_directory"]
    tools.config["test_report_directory"] = tmpdir
    try:
        yield tmpdir
    finally:
        shutil.rmtree(tmpdir)
        tools.config["test_report_directory"] = prev_test_report_dir


class TestMisReportInstance(common.HttpCase):
    """ Basic integration test to exercise mis.report.instance.

    We don't check the actual results here too much as computation correctness
    should be covered by lower level unit tests.
    """

    def setUp(self):
        super(TestMisReportInstance, self).setUp()
        partner_model_id = self.env.ref("base.model_res_partner").id
        partner_create_date_field_id = self.env.ref(
            "base.field_res_partner_create_date"
        ).id
        partner_debit_field_id = self.env.ref("account.field_res_partner_debit").id
        # create a report with 2 subkpis and one query
        self.report = self.env["mis.report"].create(
            dict(
                name="test report",
                subkpi_ids=[
                    (0, 0, dict(name="sk1", description="subkpi 1", sequence=1)),
                    (0, 0, dict(name="sk2", description="subkpi 2", sequence=2)),
                ],
                query_ids=[
                    (
                        0,
                        0,
                        dict(
                            name="partner",
                            model_id=partner_model_id,
                            field_ids=[(4, partner_debit_field_id, None)],
                            date_field=partner_create_date_field_id,
                            aggregate="sum",
                        ),
                    )
                ],
            )
        )
        # create another report with 2 subkpis, no query
        self.report_2 = self.env["mis.report"].create(
            dict(
                name="another test report",
                subkpi_ids=[
                    (
                        0,
                        0,
                        dict(
                            name="subkpi1_report2",
                            description="subkpi 1, report 2",
                            sequence=1,
                        ),
                    ),
                    (
                        0,
                        0,
                        dict(
                            name="subkpi2_report2",
                            description="subkpi 2, report 2",
                            sequence=2,
                        ),
                    ),
                ],
            )
        )
        # Third report, 2 subkpis, no query
        self.report_3 = self.env["mis.report"].create(
            dict(
                name="test report 3",
                subkpi_ids=[
                    (
                        0,
                        0,
                        dict(
                            name="subkpi1_report3",
                            description="subkpi 1, report 3",
                            sequence=1,
                        ),
                    ),
                    (
                        0,
                        0,
                        dict(
                            name="subkpi2_report3",
                            description="subkpi 2, report 3",
                            sequence=2,
                        ),
                    ),
                ],
            )
        )
        # kpi with accounting formulas
        self.kpi1 = self.env["mis.report.kpi"].create(
            dict(
                report_id=self.report.id,
                description="kpi 1",
                name="k1",
                multi=True,
                expression_ids=[
                    (
                        0,
                        0,
                        dict(name="bale[200%]", subkpi_id=self.report.subkpi_ids[0].id),
                    ),
                    (
                        0,
                        0,
                        dict(name="balp[200%]", subkpi_id=self.report.subkpi_ids[1].id),
                    ),
                ],
            )
        )
        # kpi with accounting formula and query
        self.kpi2 = self.env["mis.report.kpi"].create(
            dict(
                report_id=self.report.id,
                description="kpi 2",
                name="k2",
                multi=True,
                expression_ids=[
                    (
                        0,
                        0,
                        dict(name="balp[200%]", subkpi_id=self.report.subkpi_ids[0].id),
                    ),
                    (
                        0,
                        0,
                        dict(
                            name="partner.debit", subkpi_id=self.report.subkpi_ids[1].id
                        ),
                    ),
                ],
            )
        )
        # kpi with a simple expression summing other multi-valued kpis
        self.env["mis.report.kpi"].create(
            dict(
                report_id=self.report.id,
                description="kpi 4",
                name="k4",
                multi=False,
                expression="k1 + k2 + k3",
            )
        )
        # kpi with 2 constants
        self.env["mis.report.kpi"].create(
            dict(
                report_id=self.report.id,
                description="kpi 3",
                name="k3",
                multi=True,
                expression_ids=[
                    (
                        0,
                        0,
                        dict(
                            name="AccountingNone",
                            subkpi_id=self.report.subkpi_ids[0].id,
                        ),
                    ),
                    (0, 0, dict(name="1.0", subkpi_id=self.report.subkpi_ids[1].id)),
                ],
            )
        )
        # kpi with a NameError (x not defined)
        self.env["mis.report.kpi"].create(
            dict(
                report_id=self.report.id,
                description="kpi 5",
                name="k5",
                multi=True,
                expression_ids=[
                    (0, 0, dict(name="x", subkpi_id=self.report.subkpi_ids[0].id)),
                    (0, 0, dict(name="1.0", subkpi_id=self.report.subkpi_ids[1].id)),
                ],
            )
        )
        # string-type kpi
        self.env["mis.report.kpi"].create(
            dict(
                report_id=self.report.id,
                description="kpi 6",
                name="k6",
                multi=True,
                type=TYPE_STR,
                expression_ids=[
                    (0, 0, dict(name='"bla"', subkpi_id=self.report.subkpi_ids[0].id)),
                    (
                        0,
                        0,
                        dict(name='"blabla"', subkpi_id=self.report.subkpi_ids[1].id),
                    ),
                ],
            )
        )
        # kpi that references another subkpi by name
        self.env["mis.report.kpi"].create(
            dict(
                report_id=self.report.id,
                description="kpi 7",
                name="k7",
                multi=True,
                expression_ids=[
                    (0, 0, dict(name="k3.sk1", subkpi_id=self.report.subkpi_ids[0].id)),
                    (0, 0, dict(name="k3.sk2", subkpi_id=self.report.subkpi_ids[1].id)),
                ],
            )
        )
        # Report 2 : kpi with AccountingNone value
        self.env["mis.report.kpi"].create(
            dict(
                report_id=self.report_2.id,
                description="AccountingNone kpi",
                name="AccountingNoneKPI",
                multi=False,
            )
        )
        # Report 2 : 'classic' kpi with values for each sub-KPI
        self.env["mis.report.kpi"].create(
            dict(
                report_id=self.report_2.id,
                description="Classic kpi",
                name="classic_kpi_r2",
                multi=True,
                expression_ids=[
                    (
                        0,
                        0,
                        dict(
                            name="bale[200%]", subkpi_id=self.report_2.subkpi_ids[0].id
                        ),
                    ),
                    (
                        0,
                        0,
                        dict(
                            name="balp[200%]", subkpi_id=self.report_2.subkpi_ids[1].id
                        ),
                    ),
                ],
            )
        )
        # Report 3 : kpi with wrong tuple length
        self.env["mis.report.kpi"].create(
            dict(
                report_id=self.report_3.id,
                description="Wrong tuple length kpi",
                name="wrongTupleLen",
                multi=False,
                expression="('hello', 'does', 'this', 'work')",
            )
        )
        # Report 3 : 'classic' kpi
        self.env["mis.report.kpi"].create(
            dict(
                report_id=self.report_3.id,
                description="Classic kpi",
                name="classic_kpi_r2",
                multi=True,
                expression_ids=[
                    (
                        0,
                        0,
                        dict(
                            name="bale[200%]", subkpi_id=self.report_3.subkpi_ids[0].id
                        ),
                    ),
                    (
                        0,
                        0,
                        dict(
                            name="balp[200%]", subkpi_id=self.report_3.subkpi_ids[1].id
                        ),
                    ),
                ],
            )
        )
        # create a report instance
        self.report_instance = self.env["mis.report.instance"].create(
            dict(
                name="test instance",
                report_id=self.report.id,
                company_id=self.env.ref("base.main_company").id,
                period_ids=[
                    (
                        0,
                        0,
                        dict(
                            name="p1",
                            mode="relative",
                            type="d",
                            subkpi_ids=[(4, self.report.subkpi_ids[0].id, None)],
                        ),
                    ),
                    (
                        0,
                        0,
                        dict(
                            name="p2",
                            mode="fix",
                            manual_date_from="2014-01-01",
                            manual_date_to="2014-12-31",
                        ),
                    ),
                ],
            )
        )
        self.report_instance.period_ids[1].comparison_column_ids = [
            (4, self.report_instance.period_ids[0].id, None)
        ]
        # same for report 2
        self.report_instance_2 = self.env["mis.report.instance"].create(
            dict(
                name="test instance 2",
                report_id=self.report_2.id,
                company_id=self.env.ref("base.main_company").id,
                period_ids=[
                    (
                        0,
                        0,
                        dict(
                            name="p3",
                            mode="fix",
                            manual_date_from="2019-01-01",
                            manual_date_to="2019-12-31",
                        ),
                    )
                ],
            )
        )
        # and for report 3
        self.report_instance_3 = self.env["mis.report.instance"].create(
            dict(
                name="test instance 3",
                report_id=self.report_3.id,
                company_id=self.env.ref("base.main_company").id,
                period_ids=[
                    (
                        0,
                        0,
                        dict(
                            name="p4",
                            mode="fix",
                            manual_date_from="2019-01-01",
                            manual_date_to="2019-12-31",
                        ),
                    )
                ],
            )
        )

    def test_compute(self):
        matrix = self.report_instance._compute_matrix()
        for row in matrix.iter_rows():
            vals = [c.val for c in row.iter_cells()]
            if row.kpi.name == "k3":
                # k3 is constant
                self.assertEquals(vals, [AccountingNone, AccountingNone, 1.0])
            elif row.kpi.name == "k6":
                # k6 is a string kpi
                self.assertEquals(vals, ["bla", "bla", "blabla"])
            elif row.kpi.name == "k7":
                # k7 references k3 via subkpi names
                self.assertEquals(vals, [AccountingNone, AccountingNone, 1.0])

    def test_multi_company_compute(self):
        self.report_instance.write(
            {
                "multi_company": True,
                "company_ids": [(6, 0, self.report_instance.company_id.ids)],
            }
        )
        self.report_instance.report_id.kpi_ids.write({"auto_expand_accounts": True})
        matrix = self.report_instance._compute_matrix()
        for row in matrix.iter_rows():
            if row.account_id:
                account = self.env["account.account"].browse(row.account_id)
                self.assertEqual(
                    row.label,
                    "%s %s [%s]"
                    % (account.code, account.name, account.company_id.name),
                )
        self.report_instance.write({"multi_company": False})
        matrix = self.report_instance._compute_matrix()
        for row in matrix.iter_rows():
            if row.account_id:
                account = self.env["account.account"].browse(row.account_id)
                self.assertEqual(row.label, "{} {}".format(account.code, account.name))

    def test_evaluate(self):
        company = self.env.ref("base.main_company")
        aep = self.report._prepare_aep(company)
        r = self.report.evaluate(aep, date_from="2014-01-01", date_to="2014-12-31")
        self.assertEqual(r["k3"], (AccountingNone, 1.0))
        self.assertEqual(r["k6"], ("bla", "blabla"))
        self.assertEqual(r["k7"], (AccountingNone, 1.0))

    def test_json(self):
        self.report_instance.compute()

    def test_drilldown(self):
        action = self.report_instance.drilldown(
            dict(expr="balp[200%]", period_id=self.report_instance.period_ids[0].id)
        )
        account_ids = (
            self.env["account.account"].search([("code", "=like", "200%")]).ids
        )
        self.assertTrue(("account_id", "in", tuple(account_ids)) in action["domain"])
        self.assertEqual(action["res_model"], "account.move.line")

    def test_qweb(self):
        with enable_test_report_directory():
            self.report_instance.print_pdf()  # get action
            test_reports.try_report(
                self.env.cr,
                self.env.uid,
                "mis_builder.report_mis_report_instance",
                [self.report_instance.id],
                report_type="qweb-pdf",
            )

    def test_xlsx(self):
        with enable_test_report_directory():
            self.report_instance.export_xls()  # get action
            test_reports.try_report(
                self.env.cr,
                self.env.uid,
                "mis.report.instance.xlsx",
                [self.report_instance.id],
                report_type="xlsx",
            )

    def test_get_kpis_by_account_id(self):
        account_ids = (
            self.env["account.account"].search([("code", "=like", "200%")]).mapped("id")
        )
        kpi200 = {self.kpi1, self.kpi2}
        res = self.report.get_kpis_by_account_id(self.env.ref("base.main_company"))
        for account_id in account_ids:
            self.assertTrue(account_id in res)
            self.assertEquals(res[account_id], kpi200)

    def test_kpi_name_get_name_search(self):
        r = self.env["mis.report.kpi"].name_search("k1")
        self.assertEqual(len(r), 1)
        self.assertEqual(r[0][0], self.kpi1.id)
        self.assertEqual(r[0][1], "kpi 1 (k1)")
        r = self.env["mis.report.kpi"].name_search("kpi 1")
        self.assertEqual(len(r), 1)
        self.assertEqual(r[0][0], self.kpi1.id)
        self.assertEqual(r[0][1], "kpi 1 (k1)")

    def test_kpi_expr_name_get_name_search(self):
        r = self.env["mis.report.kpi.expression"].name_search("k1")
        self.assertEqual(
            [i[1] for i in r],
            ["kpi 1 / subkpi 1 (k1.sk1)", "kpi 1 / subkpi 2 (k1.sk2)"],
        )
        r = self.env["mis.report.kpi.expression"].name_search("k1.sk1")
        self.assertEqual([i[1] for i in r], ["kpi 1 / subkpi 1 (k1.sk1)"])
        r = self.env["mis.report.kpi.expression"].name_search("k4")
        self.assertEqual([i[1] for i in r], ["kpi 4 (k4)"])

    def test_multi_company_onchange(self):
        # not multi company
        self.assertTrue(self.report_instance.company_id)
        self.assertFalse(self.report_instance.multi_company)
        self.assertFalse(self.report_instance.company_ids)
        self.assertEqual(
            self.report_instance.query_company_ids[0], self.report_instance.company_id
        )
        # create a child company
        self.env["res.company"].create(
            dict(name="company 2", parent_id=self.report_instance.company_id.id)
        )
        companies = self.env["res.company"].search(
            [("id", "child_of", self.report_instance.company_id.id)]
        )
        self.report_instance.multi_company = True
        # multi company, company_ids not set
        self.assertEqual(
            self.report_instance.query_company_ids[0], self.report_instance.company_id
        )
        # set company_ids
        self.report_instance._onchange_company()
        self.assertTrue(self.report_instance.multi_company)
        self.assertEqual(self.report_instance.company_ids, companies)
        self.assertEqual(self.report_instance.query_company_ids, companies)
        # reset single company mode
        self.report_instance.multi_company = False
        self.assertEqual(
            self.report_instance.query_company_ids[0], self.report_instance.company_id
        )
        self.report_instance._onchange_company()
        self.assertFalse(self.report_instance.company_ids)

    def test_mis_report_analytic_filters(self):
        # Check that matrix has no values when using a filter with a non
        # existing account
        matrix = self.report_instance.with_context(
            mis_report_filters={"analytic_account_id": {"value": 999}}
        )._compute_matrix()
        for row in matrix.iter_rows():
            vals = [c.val for c in row.iter_cells()]
            if row.kpi.name == "k1":
                self.assertEquals(
                    vals, [AccountingNone, AccountingNone, AccountingNone]
                )
            elif row.kpi.name == "k2":
                self.assertEquals(vals, [AccountingNone, AccountingNone, None])
            elif row.kpi.name == "k4":
                self.assertEquals(vals, [AccountingNone, AccountingNone, 1.0])

    def test_raise_when_unknown_kpi_value_type(self):
        with self.assertRaises(SubKPIUnknownTypeError):
            self.report_instance_2.compute()

    def test_raise_when_wrong_tuple_length_with_subkpis(self):
        with self.assertRaises(SubKPITupleLengthError):
            self.report_instance_3.compute()
