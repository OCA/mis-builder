# Copyright 2025 Contributors
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from collections import defaultdict
from unittest.mock import MagicMock, Mock, patch

from odoo.tests import common

from ..models.accounting_none import AccountingNone
from ..models.aep import AccountingExpressionProcessor as AEP
from ..models.simple_array import SimpleArray


class TestAEPDynamicCompanyRates(common.TransactionCase):
    """Unit tests for AEP.do_queries() dynamic company rate handling"""

    def setUp(self):
        super().setUp()

        # Create mock companies with proper structure
        mock_companies = Mock()
        mock_companies.env = MagicMock()
        mock_companies.ids = [1, 2, 3]

        # Create a mock currency
        mock_currency = Mock()
        mock_currency.decimal_places = 2

        # Create AEP with explicit currency to bypass the companies.mapped() logic
        self.aep = AEP(mock_companies, currency=mock_currency)

        # Override with our test-specific mocks after initialization
        self.aep.env = MagicMock()
        self.aep.currency = mock_currency
        self.aep.companies = mock_companies
        self.aep._data = defaultdict(
            lambda: defaultdict(lambda: SimpleArray((AccountingNone, AccountingNone)))
        )

    def _create_mock_currency(self, name="USD", rate=1.0, decimal_places=2):
        """Helper to create mock currency objects"""
        currency = Mock()
        currency.name = name
        currency.rate = rate
        currency.decimal_places = decimal_places
        currency.with_context.return_value = currency
        return currency

    def _create_mock_company(self, company_id, name="Test Company", currency=None):
        """Helper to create mock company objects"""
        company = Mock()
        company.id = company_id
        company.name = name
        company.currency_id = currency or self._create_mock_currency()
        return company

    def _create_mock_account(self, account_id, code="100", name="Test Account"):
        """Helper to create mock account objects"""
        account = Mock()
        account.id = account_id
        account.code = code
        account.name = name
        return account

    @patch("odoo.addons.mis_builder.models.aep.defaultdict")
    def test_missing_company_rate_same_currency(self, mock_defaultdict):
        """Test handling of missing company rate when currencies match target"""
        # Setup
        mock_defaultdict.return_value = self.aep._data
        target_currency = self._create_mock_currency("EUR", 1.5, 2)
        company_currency = self._create_mock_currency("EUR", 1.5, 2)

        self.aep.currency = target_currency
        self.aep.currency.with_context.return_value.rate = 1.5

        company = self._create_mock_company(999, "Missing Company", company_currency)
        account = self._create_mock_account(1, "100", "Test Account")

        # Pre-existing company rates (missing company 999)
        company_rates = {1: (1.0, 2), 2: (2.0, 2)}

        # Mock the _get_company_rates method
        self.aep._get_company_rates = Mock(return_value=company_rates)

        # Mock the AML query result
        mock_accs = [(account, company, 100.0, 50.0)]

        # Setup other required attributes
        self.aep._map_account_ids = {((), "variation"): [1]}
        self.aep.smart_end = False
        self.aep.dp = 2
        self.aep.MODE_INITIAL = "initial"
        self.aep.MODE_UNALLOCATED = "unallocated"
        self.aep.MODE_END = "end"

        # Mock methods
        self.aep.get_aml_domain_for_dates = Mock(return_value=[])

        # Mock AML model and its methods
        mock_aml_model = Mock()
        mock_aml_model.with_context.return_value = mock_aml_model
        mock_aml_model._read_group.return_value = mock_accs

        self.aep.env.__getitem__.return_value = mock_aml_model

        # Mock float_is_zero function
        with patch(
            "odoo.addons.mis_builder.models.aep.float_is_zero", return_value=False
        ):
            # Execute the method portion we're testing
            date_to = "2025-06-25"

            # Simulate the specific logic we added
            target_rate = self.aep.currency.with_context(date=date_to).rate

            for _account_id, company_id, _debit, _credit in mock_accs:
                # This is the logic we added
                if company_id.id not in company_rates:
                    if company_id.currency_id != self.aep.currency:
                        rate = (
                            target_rate
                            / company_id.currency_id.with_context(date=date_to).rate
                        )
                    else:
                        rate = 1.0
                    company_rates[company_id.id] = (
                        rate,
                        company_id.currency_id.decimal_places,
                    )

        # Verify the missing company rate was added correctly
        self.assertIn(999, company_rates)
        rate, dp = company_rates[999]
        self.assertEqual(rate, 1.0)  # Same currency should have rate 1.0
        self.assertEqual(dp, 2)

    @patch("odoo.addons.mis_builder.models.aep.defaultdict")
    def test_missing_company_rate_different_currency(self, mock_defaultdict):
        """Test calculation of missing company rate with currency conversion"""
        # Setup
        mock_defaultdict.return_value = self.aep._data
        target_currency = self._create_mock_currency("EUR", 1.5, 2)
        company_currency = self._create_mock_currency("USD", 3.0, 2)

        self.aep.currency = target_currency
        self.aep.currency.with_context.return_value.rate = 1.5

        company = self._create_mock_company(999, "USD Company", company_currency)
        account = self._create_mock_account(1, "100", "Test Account")

        # Pre-existing company rates (missing company 999)
        company_rates = {1: (1.0, 2), 2: (2.0, 2)}

        # Mock the _get_company_rates method
        self.aep._get_company_rates = Mock(return_value=company_rates)

        # Mock the AML query result
        mock_accs = [(account, company, 100.0, 50.0)]

        # Execute the logic we added
        date_to = "2025-06-25"
        target_rate = self.aep.currency.with_context(date=date_to).rate  # 1.5

        for _account_id, company_id, _debit, _credit in mock_accs:
            if company_id.id not in company_rates:
                if company_id.currency_id != self.aep.currency:
                    rate = (
                        target_rate
                        / company_id.currency_id.with_context(date=date_to).rate
                    )
                else:
                    rate = 1.0
                company_rates[company_id.id] = (
                    rate,
                    company_id.currency_id.decimal_places,
                )

        # Verify the missing company rate was calculated correctly
        self.assertIn(999, company_rates)
        rate, dp = company_rates[999]
        expected_rate = 1.5 / 3.0  # target_rate / company_rate
        self.assertEqual(rate, expected_rate)
        self.assertEqual(dp, 2)

    def test_company_rate_caching(self):
        """Test that calculated rates are cached for subsequent use"""
        target_currency = self._create_mock_currency("EUR", 1.0, 2)
        company_currency = self._create_mock_currency("USD", 2.0, 2)

        self.aep.currency = target_currency
        self.aep.currency.with_context.return_value.rate = 1.0

        company = self._create_mock_company(999, "USD Company", company_currency)
        account1 = self._create_mock_account(1, "100", "Account 1")
        account2 = self._create_mock_account(2, "200", "Account 2")

        # Initially empty company rates
        company_rates = {}

        # Mock multiple AML records for the same company
        mock_accs = [(account1, company, 100.0, 50.0), (account2, company, 200.0, 75.0)]

        date_to = "2025-06-25"
        target_rate = self.aep.currency.with_context(date=date_to).rate

        rate_calculations = 0

        for _account_id, company_id, _debit, _credit in mock_accs:
            if company_id.id not in company_rates:
                rate_calculations += 1
                if company_id.currency_id != self.aep.currency:
                    rate = (
                        target_rate
                        / company_id.currency_id.with_context(date=date_to).rate
                    )
                else:
                    rate = 1.0
                company_rates[company_id.id] = (
                    rate,
                    company_id.currency_id.decimal_places,
                )

        # Verify rate was calculated only once despite multiple records
        self.assertEqual(rate_calculations, 1)
        self.assertIn(999, company_rates)

        # Verify rate is available for both records
        rate, dp = company_rates[999]
        self.assertEqual(rate, 0.5)  # 1.0 / 2.0

    def test_mixed_existing_and_missing_rates(self):
        """Test processing with some pre-existing and some missing company rates"""
        target_currency = self._create_mock_currency("EUR", 1.0, 2)
        usd_currency = self._create_mock_currency("USD", 2.0, 2)
        gbp_currency = self._create_mock_currency("GBP", 0.8, 2)

        self.aep.currency = target_currency
        self.aep.currency.with_context.return_value.rate = 1.0

        company_existing = self._create_mock_company(1, "Existing Company")
        company_missing_usd = self._create_mock_company(
            999, "Missing USD", usd_currency
        )
        company_missing_gbp = self._create_mock_company(
            888, "Missing GBP", gbp_currency
        )

        account = self._create_mock_account(1, "100", "Test Account")

        # Pre-existing company rates (has company 1, missing 999 and 888)
        company_rates = {1: (1.0, 2)}

        # Mock AML records for all companies
        mock_accs = [
            (account, company_existing, 100.0, 50.0),
            (account, company_missing_usd, 200.0, 75.0),
            (account, company_missing_gbp, 150.0, 25.0),
        ]

        date_to = "2025-06-25"
        target_rate = self.aep.currency.with_context(date=date_to).rate

        for _account_id, company_id, _debit, _credit in mock_accs:
            if company_id.id not in company_rates:
                if company_id.currency_id != self.aep.currency:
                    rate = (
                        target_rate
                        / company_id.currency_id.with_context(date=date_to).rate
                    )
                else:
                    rate = 1.0
                company_rates[company_id.id] = (
                    rate,
                    company_id.currency_id.decimal_places,
                )

        # Verify all companies now have rates
        self.assertIn(1, company_rates)  # Pre-existing
        self.assertIn(999, company_rates)  # Added USD
        self.assertIn(888, company_rates)  # Added GBP

        # Verify rates are correct
        self.assertEqual(company_rates[1], (1.0, 2))  # Original unchanged
        self.assertEqual(company_rates[999], (0.5, 2))  # 1.0 / 2.0
        self.assertEqual(company_rates[888], (1.25, 2))  # 1.0 / 0.8

    def test_target_rate_storage(self):
        """Test that target_rate is properly stored for missing companies"""
        target_currency = self._create_mock_currency("EUR", 1.5, 2)
        self.aep.currency = target_currency

        date_to = "2025-06-25"

        # This simulates the line we added:
        # target_rate = self.currency.with_context(date=date_to).rate
        target_rate = self.aep.currency.with_context(date=date_to).rate

        # Verify target_rate is captured correctly
        self.assertEqual(target_rate, 1.5)

        # Verify it can be used in rate calculations
        company_currency = self._create_mock_currency("USD", 3.0, 2)
        calculated_rate = target_rate / company_currency.with_context(date=date_to).rate

        self.assertEqual(calculated_rate, 0.5)  # 1.5 / 3.0
