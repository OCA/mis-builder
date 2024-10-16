from odoo import api, fields, models


class AccountFiscalPeriod(models.Model):
    _inherit = "account.fiscal.year"  # Adjust based on your needs

    # Selection field to include 'Quarter'
    period_type = fields.Selection(
        [("monthly", "Monthly"), ("quarterly", "Quarterly"), ("yearly", "Yearly")],
        string="Period Type",
        default="monthly",
        required=True,
    )

    quarter_start_date = fields.Date(string="Quarter Start Date")
    quarter_end_date = fields.Date(string="Quarter End Date")

    @api.onchange("period_type")
    def _onchange_period_type(self):
        if self.period_type == "quarterly":
            # Auto set the quarter dates (Example: Adjust to your needs)
            today = fields.Date.today()
            current_month = today.month
            if current_month in [1, 2, 3]:
                self.quarter_start_date = fields.Date.from_string(f"{today.year}-01-01")
                self.quarter_end_date = fields.Date.from_string(f"{today.year}-03-31")
            elif current_month in [4, 5, 6]:
                self.quarter_start_date = fields.Date.from_string(f"{today.year}-04-01")
                self.quarter_end_date = fields.Date.from_string(f"{today.year}-06-30")
            elif current_month in [7, 8, 9]:
                self.quarter_start_date = fields.Date.from_string(f"{today.year}-07-01")
                self.quarter_end_date = fields.Date.from_string(f"{today.year}-09-30")
            else:
                self.quarter_start_date = fields.Date.from_string(f"{today.year}-10-01")
                self.quarter_end_date = fields.Date.from_string(f"{today.year}-12-31")
