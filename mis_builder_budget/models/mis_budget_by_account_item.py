# -*- coding: utf-8 -*-
# Copyright 2017-2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class MisBudgetByAccountItem(models.Model):

    _inherit = ["mis.budget.item.abstract", "prorata.read_group.mixin"]
    _name = "mis.budget.by.account.item"
    _description = "MIS Budget Item (by Account)"
    _order = "budget_id, date_from, account_id"

    budget_id = fields.Many2one(comodel_name="mis.budget.by.account")
    debit = fields.Monetary(default=0.0, currency_field="company_currency_id")
    credit = fields.Monetary(default=0.0, currency_field="company_currency_id")
    balance = fields.Monetary(
        compute="_compute_balance", store=True, currency_field="company_currency_id"
    )
    company_id = fields.Many2one(
        "res.company",
        related="budget_id.company_id",
        readonly=True,
        store=True,
    )
    company_currency_id = fields.Many2one(
        "res.currency",
        related="budget_id.company_id.currency_id",
        string="Company Currency",
        readonly=True,
        help="Utility field to express amount currency",
        store=True,
    )
    account_id = fields.Many2one(
        comodel_name="account.account",
        string="Account",
        required=True,
        # TODO domain (company_id)
    )

    _sql_constraints = [
        (
            "credit_debit1",
            "CHECK (credit*debit=0)",
            "Wrong credit or debit value in budget item! "
            "Credit or debit should be zero.",
        ),
        (
            "credit_debit2",
            "CHECK (credit+debit>=0)",
            "Wrong credit or debit value in budget item! "
            "Credit and debit should be positive.",
        ),
    ]

    @api.depends("debit", "credit")
    def _compute_balance(self):
        for rec in self:
            rec.balance = rec.debit - rec.credit

    def _prepare_overlap_domain(self):
        """Prepare a domain to check for overlapping budget items."""
        domain = super(MisBudgetByAccountItem, self)._prepare_overlap_domain()
        domain.extend([("account_id", "=", self.account_id.id)])
        return domain

    @api.constrains(
        "date_range_id",
        "date_from",
        "date_to",
        "budget_id",
        "analytic_account_id",
        "analytic_tag_ids",
        "account_id",
    )
    def _check_dates(self):
        super(MisBudgetByAccountItem, self)._check_dates()
