# Copyright 2025 Geraldo Lopez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from unittest.mock import MagicMock, Mock

from odoo.tests import common

from ..models.kpimatrix import COMPANY_NAMES_DISPLAY_LIMIT, KpiMatrix


class TestKPIMatrixAccountNames(common.TransactionCase):
    """Unit tests for KpiMatrix._get_account_name() method enhancements"""

    def _create_mock_env_kpimatrix(self, companies):
        """Helper to create KpiMatrix instances"""
        # Create a proper mock environment for KpiMatrix
        mock_env = MagicMock()
        # Mock the required models and services
        mock_lang_model = Mock()
        mock_lang_model._lang_get.return_value = Mock()
        mock_env.__getitem__.side_effect = lambda key: {
            "res.lang": mock_lang_model,
            "mis.report.style": Mock(),
            "account.account": Mock(),
        }.get(key, Mock())
        # Mock user with language
        mock_env.user.lang = "en_US"
        mock_env._ = self.env._
        # Create KpiMatrix instance with chosen companies
        return KpiMatrix(
            mock_env, multi_company=len(companies) > 1, query_companies=companies
        )

    def _create_mock_account(self, code, name, company_ids):
        """Helper to create mock account objects"""
        account = Mock()
        account.code = code
        account.name = name
        account.company_ids = company_ids or []
        return account

    def _create_nbr_companies(self, number_of_companies):
        """Helper to create company objects"""
        companies = self.env["res.company"]
        for name in [f"Company {i + 1}" for i in range(number_of_companies)]:
            companies |= self.env["res.company"].create({"name": name})
        return companies

    def test_get_account_name_single_company(self):
        """Test account name without company info in single company mode"""
        company = self._create_nbr_companies(1)
        single_company_matrix = self._create_mock_env_kpimatrix(company)
        account = self._create_mock_account("100", "Cash", company)
        result = single_company_matrix._get_account_name(account)
        self.assertEqual(
            result,
            "100 Cash",
            "Account name are not displayed correctly on single company",
        )

    def test_get_account_name_with_company_ids_multiple(self):
        """Test account name with company_ids field containing multiple
        companies (≤ 3)"""
        companies = self._create_nbr_companies(COMPANY_NAMES_DISPLAY_LIMIT)
        account = self._create_mock_account("300", "Receivables", companies)
        kpi_matrix = self._create_mock_env_kpimatrix(companies)
        result = kpi_matrix._get_account_name(account)
        self.assertEqual(
            result,
            "300 Receivables [Company 1, Company 2, Company 3]",
            "Company names on account name are not displayed correctly",
        )

    def test_get_account_name_with_company_ids_many(self):
        """Test account name with company_ids field containing > N companies"""
        companies = self._create_nbr_companies(COMPANY_NAMES_DISPLAY_LIMIT + 1)
        account = self._create_mock_account("400", "Payables", companies)
        kpi_matrix = self._create_mock_env_kpimatrix(companies)
        result = kpi_matrix._get_account_name(account)
        self.assertEqual(
            result,
            "400 Payables [Company 1, Company 2, Company 3, and 1 more]",
            "Company names on account name should be truncated",
        )
