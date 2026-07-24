# Copyright 2026 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models


class MisReportAccountCoverageCheck(models.TransientModel):
    _name = "mis.report.account.coverage.check"
    _description = "Check accounts used in postings but not covered by a MIS report"

    state = fields.Selection(
        selection=[("init", "Configuration"), ("done", "Results")],
        string="Status",
        readonly=True,
        default="init",
    )
    report_instance_id = fields.Many2one(
        comodel_name="mis.report.instance",
        string="MIS Report Instance",
        required=True,
        ondelete="cascade",
    )
    period_ids = fields.Many2many(
        comodel_name="mis.report.instance.period",
        relation="mis_report_account_coverage_check_period_rel",
        string="Periods to check",
        domain="[('report_instance_id', '=', report_instance_id)]",
        help="Leave empty to check all periods of the instance.",
    )
    account_code_from = fields.Char(string="Account code from", required=True)
    account_code_to = fields.Char(string="Account code to", required=True)
    line_ids = fields.One2many(
        comodel_name="mis.report.account.coverage.check.line",
        inverse_name="check_id",
        string="Uncovered accounts",
    )

    @api.onchange("report_instance_id")
    def _onchange_report_instance_id(self):
        self.period_ids = self.report_instance_id.period_ids

    def _get_account_range_domain(self):
        self.ensure_one()
        return [
            ("code", ">=", self.account_code_from),
            ("code", "<=", self.account_code_to),
        ]

    def _get_covered_account_ids(self, aep):
        """Account ids referenced by at least one KPI expression of the
        report template, including subreport KPIs (``all_kpi_ids``, unlike
        the core ``get_kpis_by_account_id`` which only looks at ``kpi_ids``).

        Every KPI counts, including aggregate/rollup ones (e.g. a "Result
        for the year" line that nets the whole P&L with a ``6%,7%`` wildcard
        into a single equity figure): if an account is correctly summed into
        such a KPI, it does not put the report out of balance, so it must
        not be reported as uncovered even though it has no individual detail
        line of its own.
        """
        self.ensure_one()
        report = self.report_instance_id.report_id
        covered_ids = set()
        for kpi in report.all_kpi_ids:
            for expression in kpi.expression_ids:
                if expression.name:
                    covered_ids.update(aep.get_account_ids_for_expr(expression.name))
        return covered_ids

    def _reopen(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "res_model": self._name,
            "res_id": self.id,
            "view_mode": "form",
            "target": "new",
        }

    def action_check(self):
        self.ensure_one()
        self.line_ids.unlink()
        instance = self.report_instance_id
        report = instance.report_id
        account_model = self.env[report.account_model or "account.account"]
        aml_model = self.env[report.sudo().move_lines_source.model]
        aep = report._prepare_aep(instance.query_company_ids, instance.currency_id)

        range_accounts = account_model.search(
            self._get_account_range_domain()
            + [("company_id", "in", instance.query_company_ids.ids)]
        )
        covered_ids = self._get_covered_account_ids(aep)
        uncovered_accounts = range_accounts.filtered(
            lambda account: account.id not in covered_ids
        )

        line_vals = []
        if uncovered_accounts:
            periods = self.period_ids or instance.period_ids
            for period in periods:
                if not (period.date_from and period.date_to):
                    continue
                # MODE_END ("ending balance", what every balance-sheet KPI
                # expression uses): balance-sheet accounts (asset/liability
                # /equity, "include_initial_balance") are summed since the
                # beginning of time, since without formal closing/opening
                # entries their balance keeps accumulating across fiscal
                # years; P&L accounts are summed since the start of the
                # fiscal year only, since those reset every year. A plain
                # ("date", ">=", period.date_from) window would miss
                # balance-sheet accounts whose contributing postings are
                # older than the period being checked.
                domain = [
                    ("account_id", "in", uncovered_accounts.ids),
                    ("company_id", "in", instance.query_company_ids.ids),
                ]
                domain += aep.get_aml_domain_for_dates(
                    period.date_from, period.date_to, aep.MODE_END
                )
                domain += period._get_additional_move_line_filter()
                groups = aml_model.read_group(
                    domain,
                    ["account_id", "debit", "credit", "balance"],
                    ["account_id"],
                )
                for group in groups:
                    if not group["account_id"]:
                        continue
                    line_vals.append(
                        (
                            0,
                            0,
                            {
                                "period_id": period.id,
                                "account_id": group["account_id"][0],
                                "debit": group["debit"],
                                "credit": group["credit"],
                                "balance": group["balance"],
                                "move_line_count": group["account_id_count"],
                            },
                        )
                    )
        self.line_ids = line_vals
        self.state = "done"
        return self._reopen()

    def action_back(self):
        self.ensure_one()
        self.line_ids.unlink()
        self.state = "init"
        return self._reopen()
