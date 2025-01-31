from odoo import fields, models


class MisKpiDataTestItem(models.Model):
    _name = "mis.kpi.data.test.item"
    _inherit = "mis.kpi.data"
    _description = "MIS Kpi Data test item"


class ProrataReadGroupThing(models.Model):
    _name = "prorata.read.group.thing"
    _inherit = "prorata.read_group.mixin"
    _description = "Prorata Read Group Thing"

    date_from = fields.Date(required=True)
    date_to = fields.Date(required=True)
    account_code = fields.Char(required=True)
    debit = fields.Float()
    credit = fields.Float()
    company_id = fields.Many2one(
        "res.company",
        required=True,
        default=lambda self: self.env.company,
    )
