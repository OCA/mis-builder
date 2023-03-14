# Copyright 2019 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase


class TestAnalyticFilters(TransactionCase):
    def setUp(self):
        super().setUp()
        self.aaa = self.env["account.analytic.account"].search([], limit=1)

    def test_context_with_filters(self):
        aaa = self.env["account.analytic.account"].search([], limit=1)
        mri = self.env["mis.report.instance"].new()
        mri.analytic_account_id = False
        assert mri._context_with_filters().get("mis_report_filters") == {}
        mri.analytic_account_id = aaa
        assert mri._context_with_filters().get("mis_report_filters") == {
            "analytic_account_id": {"value": aaa.id, "operator": "="},
        }
        # test _context_with_filters does nothing is a filter is already
        # in the context
        assert mri.with_context(
            mis_report_filters={"f": 1}
        )._context_with_filters().get("mis_report_filters") == {"f": 1}

    def _check_get_filter_domain_from_context(
        self, mis_report_filters, expected_domain
    ):
        domain = (
            self.env["mis.report.instance.period"]
            .with_context(mis_report_filters=mis_report_filters)
            ._get_filter_domain_from_context()
        )
        assert domain == expected_domain

    def _check_get_filter_descriptions_from_context(
        self, mis_report_filters, expected_domain
    ):
        filter_descriptions = (
            self.env["mis.report.instance"]
            .with_context(mis_report_filters=mis_report_filters)
            .get_filter_descriptions_from_context()
        )
        assert filter_descriptions == expected_domain

    def test_get_filter_domain_from_context_1(self):
        # no filter, no domain
        self._check_get_filter_domain_from_context({}, [])
        # the most basic analytic account filter (default operator is =)
        self._check_get_filter_domain_from_context(
            {"analytic_account_id": {"value": 1}}, [("analytic_account_id", "=", 1)]
        )
        # custom operator
        self._check_get_filter_domain_from_context(
            {"analytic_account_id": {"value": 1, "operator": "!="}},
            [("analytic_account_id", "!=", 1)],
        )
        # any field name works
        self._check_get_filter_domain_from_context(
            {"some_field": {"value": "x"}}, [("some_field", "=", "x")]
        )
        # filter name without value => no domain
        self._check_get_filter_domain_from_context({"some_field": None}, [])
        # "is not set" filter must work
        self._check_get_filter_domain_from_context(
            {"analytic_account_id": {"value": False}},
            [("analytic_account_id", "=", False)],
        )
        # Filter from analytic account filter widget
        self._check_get_filter_domain_from_context(
            {"analytic_account_id": {"value": 1, "operator": "all"}},
            [("analytic_account_id", "in", [1])],
        )

    def test_get_filter_descriptions_from_context_1(self):
        self._check_get_filter_descriptions_from_context(
            {"analytic_account_id": {"value": self.aaa.id}},
            ["Analytic Account: %s" % self.aaa.display_name],
        )
