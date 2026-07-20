# Copyright 2017-2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class MisBudgetByAccountItem(models.Model):
    _inherit = [
        "mis.budget.item.abstract",
        "prorata.read_group.mixin",
        "analytic.mixin",
    ]
    _name = "mis.budget.by.account.item"
    _description = "MIS Budget Item (by Account)"
    _order = "budget_id, date_from, account_id"

    name = fields.Char(string="Label")
    budget_id = fields.Many2one(comodel_name="mis.budget.by.account")
    debit = fields.Monetary(default=0.0, currency_field="company_currency_id")
    credit = fields.Monetary(default=0.0, currency_field="company_currency_id")
    balance = fields.Monetary(
        compute="_compute_balance",
        inverse="_inverse_balance",
        store=True,
        currency_field="company_currency_id",
    )
    company_id = fields.Many2one(
        comodel_name="res.company",
        default=lambda self: self.env.company,
        required=True,
    )
    company_currency_id = fields.Many2one(
        "res.currency",
        related="company_id.currency_id",
        string="Company Currency",
        help="Utility field to express amount currency",
        store=True,
    )
    account_id = fields.Many2one(
        comodel_name="account.account",
        required=True,
        check_company=True,
    )

    _credit_debit_check_1 = models.Constraint(
        "CHECK (credit*debit=0)",
        "Wrong credit or debit value in budget item! Credit or debit should be zero.",
    )

    _credit_debit_check_2 = models.Constraint(
        "CHECK (credit+debit>=0)",
        "Wrong credit or debit value in budget item! "
        "Credit and debit should be positive.",
    )

    @api.depends("debit", "credit")
    def _compute_balance(self):
        for rec in self:
            rec.balance = rec.debit - rec.credit

    def _prepare_overlap_domain(self) -> list:
        """Prepare a domain to check for overlapping budget items."""
        if self.budget_id.allow_items_overlap:
            # Trick mis.budget.abstract._check_dates into never seeing
            # overlapping budget items. This "hack" is necessary because, for now,
            # overlapping budget items is only possible for budget by account items
            # and kpi budget items.
            return [("id", "=", 0)]
        domain = super()._prepare_overlap_domain()
        domain.extend([("account_id", "=", self.account_id.id)])
        return domain

    @api.constrains(
        "date_range_id",
        "date_from",
        "date_to",
        "budget_id",
        "account_id",
    )
    def _check_dates(self):
        return super()._check_dates()

    def _inverse_balance(self):
        for rec in self:
            if rec.balance < 0:
                rec.credit = -rec.balance
                rec.debit = 0
            else:
                rec.credit = 0
                rec.debit = rec.balance
