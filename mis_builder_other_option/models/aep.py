import re

from odoo.tools.safe_eval import datetime, dateutil, safe_eval, time

from odoo.addons.mis_builder.models.aep import (
    AccountingExpressionProcessor as AEP,
    _is_domain,
)


class AccountingExpressionProcessor(AEP):
    """
    Code taken from
        mis_builder/models/aep.py
    as of

    commit cd7990901b51b73c8ef7dc105a5b4e392384463d
    Date:   Mon Feb 13 19:16:49 2023 +0000

    We make the original point to this, and then make sure the super
    is calling the correct super!
    """

    def _parse_match_object_modified(self, mo):
        """Split a match object corresponding to an accounting variable

        Returns field, mode, account domain, move line domain.
        """
        domain_eval_context = {
            "ref": self.env.ref,
            "user": self.env.user,
            "time": time,
            "datetime": datetime,
            "dateutil": dateutil,
        }

        # Modified
        # ==============================================================================
        # field, mode, account_sel, ml_domain = mo.groups()
        field, mode, account_sel, ml_domain, options = mo.groups()
        self.mis_options = options and safe_eval(options, domain_eval_context) or {}
        # ==============================================================================

        # handle some legacy modes
        if not mode:
            mode = self.MODE_VARIATION
        elif mode == "s":
            mode = self.MODE_END
        # convert account selector to account domain
        if account_sel.startswith("_"):
            # legacy bal_NNN%
            acc_domain = self._account_codes_to_domain(account_sel[1:])
        else:
            assert account_sel[0] == "[" and account_sel[-1] == "]"
            inner_account_sel = account_sel[1:-1].strip()
            if not inner_account_sel:
                # empty selector: select all accounts
                acc_domain = tuple()
            elif _is_domain(inner_account_sel):
                # account selector is a domain
                acc_domain = tuple(safe_eval(account_sel, domain_eval_context))
            else:
                # account selector is a list of account codes
                acc_domain = self._account_codes_to_domain(inner_account_sel)
        # move line domain
        if ml_domain:
            assert ml_domain[0] == "[" and ml_domain[-1] == "]"
            ml_domain = tuple(safe_eval(ml_domain, domain_eval_context))
        else:
            ml_domain = tuple()
        return field, mode, acc_domain, ml_domain

    # Added new options
    _ACC_RE_NEW = re.compile(AEP._ACC_RE.pattern + r"\s*(?P<options>\{.*?\})?")


AEP._ACC_RE = AccountingExpressionProcessor._ACC_RE_NEW
AEP._parse_match_object = AccountingExpressionProcessor._parse_match_object_modified
