# Copyright 2025 Geraldo Lopez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from unittest.mock import MagicMock, Mock

from odoo.tests import common

from ..models.kpimatrix import KpiMatrix


class TestKPIMatrixAccountNames(common.TransactionCase):
    """Unit tests for KpiMatrix._get_account_name() method enhancements"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

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

        # Create KpiMatrix with mock environment
        cls.kpi_matrix = KpiMatrix(mock_env, multi_company=True)

    def _create_mock_account(
        self,
        code="100",
        name="Test Account",
        company_ids=None,
    ):
        """Helper to create mock account objects"""
        account = Mock()
        account.code = code
        account.name = name

        account.company_ids = company_ids or []

        return account

    def _create_mock_company(self, name):
        """Helper to create mock company objects"""
        company = Mock()
        company.name = name
        return company

    def test_get_account_name_single_company_mode(self):
        """Test account name without company info in single company mode"""
        # Create a separate KpiMatrix for single company mode
        mock_env = MagicMock()
        mock_lang_model = Mock()
        mock_lang_model._lang_get.return_value = Mock()
        mock_env.__getitem__.side_effect = lambda key: {
            "res.lang": mock_lang_model,
            "mis.report.style": Mock(),
            "account.account": Mock(),
        }.get(key, Mock())
        mock_env.user.lang = "en_US"

        single_company_matrix = KpiMatrix(mock_env, multi_company=False)

        account = self._create_mock_account(code="100", name="Cash")

        result = single_company_matrix._get_account_name(account)

        self.assertEqual(result, "100 Cash")

    def test_get_account_name_with_company_ids_single(self):
        """Test account name with company_ids field containing one company"""
        company = self._create_mock_company("Company B")
        account = self._create_mock_account(
            code="200",
            name="Bank",
            company_ids=[company],
        )

        result = self.kpi_matrix._get_account_name(account)
        self.assertEqual(result, "200 Bank [Company B]")

    def test_get_account_name_with_company_ids_multiple(self):
        """Test account name with company_ids field containing multiple
        companies (≤3)"""
        companies = [
            self._create_mock_company("Company A"),
            self._create_mock_company("Company B"),
            self._create_mock_company("Company C"),
        ]

        account = self._create_mock_account(
            code="300",
            name="Receivables",
            company_ids=companies,
        )

        result = self.kpi_matrix._get_account_name(account)
        self.assertEqual(result, "300 Receivables [Company A, Company B, Company C]")

    def test_get_account_name_with_company_ids_many(self):
        """Test account name with company_ids field containing >3 companies
        (should truncate)"""
        companies = [
            self._create_mock_company("Company A"),
            self._create_mock_company("Company B"),
            self._create_mock_company("Company C"),
            self._create_mock_company("Company D"),
            self._create_mock_company("Company E"),
        ]

        account = self._create_mock_account(
            code="400",
            name="Payables",
            company_ids=companies,
        )

        result = self.kpi_matrix._get_account_name(account)
        self.assertEqual(result, "400 Payables [Company A, Company B, Company C, ...]")
