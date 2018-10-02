# -*- coding: utf-8 -*-
# Copyright 2017-2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import os
from os.path import join as opj

from odoo import api, fields, models, tools


class MisCommittedPurchase(models.Model):

    _name = 'mis.committed.purchase'
    _description = 'MIS Committed Purchase'
    _auto = False

    line_type = fields.Char()
    name = fields.Char()
    analytic_account_id = fields.Many2one(
        comodel_name='account.analytic.account',
        string="Analytic Account",
    )
    account_id = fields.Many2one(
        comodel_name='account.account',
        string='Account',
    )
    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Company',
    )
    credit = fields.Float()
    debit = fields.Float()
    date = fields.Date()

    @api.model_cr
    def init(self):
        script = opj(os.path.dirname(__file__), 'mis_committed_purchase.sql')
        with open(script) as f:
            tools.drop_view_if_exists(self.env.cr, 'mis_committed_purchase')
            self.env.cr.execute(f.read())
