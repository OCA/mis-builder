# Copyright 2021 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from collections import defaultdict

from odoo.models import expression
from odoo.tools.float_utils import float_is_zero

from odoo.addons.mis_builder.models.accounting_none import AccountingNone
from odoo.addons.mis_builder.models.aep import AccountingExpressionProcessor


class AccountingExpressionProcessorActivity(AccountingExpressionProcessor):
    def do_queries(
        self,
        date_from,
        date_to,
        target_move="posted",
        additional_move_line_filter=None,
        aml_model=None,
        is_activity=False,
    ):
        """Query sums of debit and credit for all accounts and domains
        used in expressions.

        This method must be executed after done_parsing().
        """
        if not aml_model:
            aml_model = self.env["account.move.line"]
        else:
            aml_model = self.env[aml_model]
        aml_model = aml_model.with_context(active_test=False)
        company_rates = self._get_company_rates(date_to)
        # {(domain, mode): {account_id: (debit, credit)}}
        self._data = defaultdict(dict)
        domain_by_mode = {}
        ends = []
        for key in self._map_account_ids:
            domain, mode = key
            if mode == self.MODE_END and self.smart_end:
                # postpone computation of ending balance
                ends.append((domain, mode))
                continue
            if mode not in domain_by_mode:
                domain_by_mode[mode] = self.get_aml_domain_for_dates(
                    date_from, date_to, mode, target_move
                )
            domain = list(domain) + domain_by_mode[mode]
            if additional_move_line_filter:
                domain.extend(additional_move_line_filter)
            # fetch sum of debit/credit, grouped by account_id
            accs = aml_model.read_group(
                domain,
                ["activity_id", "debit", "credit", "account_id", "company_id"],
                ["activity_id", "company_id"],
                lazy=False,
            )
            for acc in accs:
                rate, dp = company_rates[acc["company_id"][0]]
                debit = acc["debit"] or 0.0
                credit = acc["credit"] or 0.0
                if mode in (self.MODE_INITIAL, self.MODE_UNALLOCATED) and float_is_zero(
                    debit - credit, precision_digits=self.dp
                ):
                    # in initial mode, ignore accounts with 0 balance
                    continue
                self._data[key][acc["activity_id"][0]] = (debit * rate, credit * rate)
        # compute ending balances by summing initial and variation
        for key in ends:
            domain, mode = key
            initial_data = self._data[(domain, self.MODE_INITIAL)]
            variation_data = self._data[(domain, self.MODE_VARIATION)]
            account_ids = set(initial_data.keys()) | set(variation_data.keys())
            for account_id in account_ids:
                di, ci = initial_data.get(account_id, (AccountingNone, AccountingNone))
                dv, cv = variation_data.get(
                    account_id, (AccountingNone, AccountingNone)
                )
                self._data[key][account_id] = (di + dv, ci + cv)

    def get_aml_domain_for_expr(
        self, expr, date_from, date_to, target_move, account_id=None
    ):
        """Get a domain on account.move.line for an expression.

        Prerequisite: done_parsing() must have been invoked.

        Returns a domain that can be used to search on account.move.line.
        """
        aml_domains = []
        date_domain_by_mode = {}
        for mo in self._ACC_RE.finditer(expr):
            field, mode, acc_domain, ml_domain = self._parse_match_object(mo)
            aml_domain = list(ml_domain)
            activity_ids = set()
            activity_ids.update(self._account_ids_by_acc_domain[acc_domain])
            if not account_id:
                aml_domain.append(("activity_id", "in", tuple(activity_ids)))
            else:
                # filter on account_id
                if account_id in activity_ids:
                    aml_domain.append(("activity_id", "=", account_id))
                else:
                    continue
            if field == "crd":
                aml_domain.append(("credit", "<>", 0.0))
            elif field == "deb":
                aml_domain.append(("debit", "<>", 0.0))
            aml_domains.append(expression.normalize_domain(aml_domain))
            if mode not in date_domain_by_mode:
                date_domain_by_mode[mode] = self.get_aml_domain_for_dates(
                    date_from, date_to, mode, target_move
                )
        assert aml_domains
        # TODO we could do this for more precision:
        #      AND(OR(aml_domains[mode]), date_domain[mode]) for each mode
        return expression.OR(aml_domains) + expression.OR(date_domain_by_mode.values())
