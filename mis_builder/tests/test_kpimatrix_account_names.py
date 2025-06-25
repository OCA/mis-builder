# Copyright 2025 Contributors
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from unittest.mock import MagicMock, Mock

from odoo.tests import common

from ..models.kpimatrix import KpiMatrix


class TestKPIMatrixAccountNames(common.TransactionCase):
    """Unit tests for KpiMatrix._get_account_name() method enhancements"""

    def setUp(self):
        super().setUp()

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
        self.kpi_matrix = KpiMatrix(mock_env, multi_company=True)

    def _create_mock_account(
        self,
        code="100",
        name="Test Account",
        company_id=None,
        company_ids=None,
        has_company_id=True,
        has_company_ids=True,
    ):
        """Helper to create mock account objects"""
        account = Mock()
        account.code = code
        account.name = name

        # Mock hasattr behavior
        def mock_hasattr(obj, attr):
            if attr == "company_id":
                return has_company_id
            elif attr == "company_ids":
                return has_company_ids
            return False

        # Patch hasattr for this test
        original_hasattr = hasattr

        def patched_hasattr(obj, attr):
            if obj is account:
                return mock_hasattr(obj, attr)
            return original_hasattr(obj, attr)

        # Set up company fields
        if has_company_id:
            account.company_id = company_id
        if has_company_ids:
            account.company_ids = company_ids or []

        return account, patched_hasattr

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

        account, _ = self._create_mock_account(code="100", name="Cash")

        result = single_company_matrix._get_account_name(account)

        self.assertEqual(result, "100 Cash")

    def test_get_account_name_with_company_id(self):
        """Test account name with traditional company_id field"""
        company = self._create_mock_company("Company A")
        account, mock_hasattr = self._create_mock_account(
            code="100", name="Cash", company_id=company, has_company_ids=False
        )

        # Patch hasattr for this test
        import builtins

        original_hasattr = builtins.hasattr
        builtins.hasattr = mock_hasattr

        try:
            result = self.kpi_matrix._get_account_name(account)
            self.assertEqual(result, "100 Cash [Company A]")
        finally:
            builtins.hasattr = original_hasattr

    def test_get_account_name_with_company_ids_single(self):
        """Test account name with company_ids field containing one company"""
        company = self._create_mock_company("Company B")
        account, mock_hasattr = self._create_mock_account(
            code="200",
            name="Bank",
            company_id=None,
            company_ids=[company],
            has_company_id=False,
        )

        import builtins

        original_hasattr = builtins.hasattr
        builtins.hasattr = mock_hasattr

        try:
            result = self.kpi_matrix._get_account_name(account)
            self.assertEqual(result, "200 Bank [Company B]")
        finally:
            builtins.hasattr = original_hasattr

    def test_get_account_name_with_company_ids_multiple(self):
        """Test account name with company_ids field containing multiple
        companies (≤3)"""
        companies = [
            self._create_mock_company("Company A"),
            self._create_mock_company("Company B"),
            self._create_mock_company("Company C"),
        ]

        account, mock_hasattr = self._create_mock_account(
            code="300",
            name="Receivables",
            company_id=None,
            company_ids=companies,
            has_company_id=False,
        )

        import builtins

        original_hasattr = builtins.hasattr
        builtins.hasattr = mock_hasattr

        try:
            result = self.kpi_matrix._get_account_name(account)
            self.assertEqual(
                result, "300 Receivables [Company A, Company B, Company C]"
            )
        finally:
            builtins.hasattr = original_hasattr

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

        account, mock_hasattr = self._create_mock_account(
            code="400",
            name="Payables",
            company_id=None,
            company_ids=companies,
            has_company_id=False,
        )

        import builtins

        original_hasattr = builtins.hasattr
        builtins.hasattr = mock_hasattr

        try:
            result = self.kpi_matrix._get_account_name(account)
            self.assertEqual(
                result, "400 Payables [Company A, Company B, Company C, ...]"
            )
        finally:
            builtins.hasattr = original_hasattr

    def test_get_account_name_no_company_fields(self):
        """Test graceful handling when neither company_id nor company_ids exist"""
        account, mock_hasattr = self._create_mock_account(
            code="500", name="Equipment", has_company_id=False, has_company_ids=False
        )

        import builtins

        original_hasattr = builtins.hasattr
        builtins.hasattr = mock_hasattr

        try:
            result = self.kpi_matrix._get_account_name(account)
            self.assertEqual(result, "500 Equipment")
        finally:
            builtins.hasattr = original_hasattr

    def test_get_account_name_empty_company_id(self):
        """Test handling when company_id exists but is empty/None"""
        account, mock_hasattr = self._create_mock_account(
            code="600", name="Inventory", company_id=None, has_company_ids=False
        )

        import builtins

        original_hasattr = builtins.hasattr
        builtins.hasattr = mock_hasattr

        try:
            result = self.kpi_matrix._get_account_name(account)
            self.assertEqual(result, "600 Inventory")
        finally:
            builtins.hasattr = original_hasattr

    def test_get_account_name_empty_company_ids(self):
        """Test handling when company_ids exists but is empty"""
        account, mock_hasattr = self._create_mock_account(
            code="700",
            name="Revenue",
            company_id=None,
            company_ids=[],
            has_company_id=False,
        )

        import builtins

        original_hasattr = builtins.hasattr
        builtins.hasattr = mock_hasattr

        try:
            result = self.kpi_matrix._get_account_name(account)
            self.assertEqual(result, "700 Revenue")
        finally:
            builtins.hasattr = original_hasattr

    def test_get_account_name_priority_company_id_over_company_ids(self):
        """Test that company_id takes priority when both fields exist"""
        company_single = self._create_mock_company("Primary Company")
        companies_multiple = [
            self._create_mock_company("Company X"),
            self._create_mock_company("Company Y"),
        ]

        account, mock_hasattr = self._create_mock_account(
            code="800",
            name="Assets",
            company_id=company_single,
            company_ids=companies_multiple,
            has_company_id=True,
            has_company_ids=True,
        )

        import builtins

        original_hasattr = builtins.hasattr
        builtins.hasattr = mock_hasattr

        try:
            result = self.kpi_matrix._get_account_name(account)
            # Should use company_id, not company_ids
            self.assertEqual(result, "800 Assets [Primary Company]")
        finally:
            builtins.hasattr = original_hasattr
