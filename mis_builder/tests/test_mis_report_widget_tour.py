# Copyright 2026 APyCOD (<https://apycod.com>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from unittest.mock import patch

import odoo.tests.common as common
from odoo.tests import tagged


@tagged("at_install", "post_install")
class TestMisReportWidgetTour(common.HttpCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        aml_model_id = cls.env.ref("account.model_account_move_line").id
        aml_date_field_id = cls.env.ref("account.field_account_move_line__date").id
        aml_debit_field_id = cls.env.ref("account.field_account_move_line__debit").id

        journal = cls.env["account.journal"].search([("type", "=", "general")], limit=1)
        account = cls.env["account.account"].search([("code", "!=", False)], limit=1)
        account.name = "Line Account"

        move = cls.env["account.move"].create(
            {
                "journal_id": journal.id,
                "date": "2026-06-01",
                "line_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "Line 1",
                            "account_id": account.id,
                            "debit": 100.0,
                            "credit": 0.0,
                            "date": "2026-06-01",
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "name": "Line 2",
                            "account_id": account.id,
                            "debit": 0.0,
                            "credit": 100.0,
                            "date": "2026-06-01",
                        },
                    ),
                ],
            }
        )
        move.action_post()

        cls.report = cls.env["mis.report"].create(
            {
                "name": "Test Drilldown Report",
                "move_lines_source": aml_model_id,
                "query_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "aml",
                            "model_id": aml_model_id,
                            "field_ids": [(4, aml_debit_field_id, None)],
                            "date_field": aml_date_field_id,
                            "aggregate": "sum",
                        },
                    )
                ],
                "kpi_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "kpi1",
                            "description": "KPI 1",
                            "expression": f"deb[{account.code}]",
                            "type": "num",
                            "sequence": 1,
                        },
                    )
                ],
            }
        )

        search_view = cls.env.ref("account.view_account_move_line_filter")

        cls.report_instance = cls.env["mis.report.instance"].create(
            {
                "name": "Test Instance Drilldown",
                "report_id": cls.report.id,
                "widget_show_filters": True,
                "widget_search_view_id": search_view.id,
                "comparison_mode": True,
                "pivot_date": "2026-06-01",
                "date_from": "2026-01-01",
                "date_to": "2026-12-31",
                "period_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "2026",
                            "mode": "fix",
                            "manual_date_from": "2026-01-01",
                            "manual_date_to": "2026-12-31",
                        },
                    )
                ],
            }
        )

    def test_mis_report_drilldown_tour(self):
        self.report_instance.widget_cache_report_on_drill_down = False
        view_id = self.env.ref("mis_builder.mis_report_instance_result_view_form").id
        url = (
            f"/web#id={self.report_instance.id}"
            f"&model=mis.report.instance"
            f"&view_type=form"
            f"&view_id={view_id}"
        )
        compute_calls = []
        model_cls = type(self.report_instance)
        orig_compute = model_cls.compute

        def mock_compute(instance_self, *args, **kwargs):
            compute_calls.append(instance_self.id)
            return orig_compute(instance_self, *args, **kwargs)

        with patch.object(
            model_cls, "compute", side_effect=mock_compute, autospec=True
        ):
            self.start_tour(url, "mis_report_drilldown_tour", login="admin")

        # Without cache: compute() is called 3 times:
        # 1. Initial form view load
        # 2. Filter search input update
        # 3. Return via breadcrumbs (recomputed)
        self.assertEqual(len(compute_calls), 3)

    def test_mis_report_drilldown_cache_tour(self):
        self.report_instance.widget_cache_report_on_drill_down = True
        view_id = self.env.ref("mis_builder.mis_report_instance_result_view_form").id
        url = (
            f"/web#id={self.report_instance.id}"
            f"&model=mis.report.instance"
            f"&view_type=form"
            f"&view_id={view_id}"
        )
        compute_calls = []
        model_cls = type(self.report_instance)
        orig_compute = model_cls.compute

        def mock_compute(instance_self, *args, **kwargs):
            compute_calls.append(instance_self.id)
            return orig_compute(instance_self, *args, **kwargs)

        with patch.object(
            model_cls, "compute", side_effect=mock_compute, autospec=True
        ):
            self.start_tour(url, "mis_report_drilldown_tour", login="admin")

        # With cache: compute() is called 2 times:
        # 1. Initial form view load
        # 2. Filter search input update
        # Return via breadcrumbs uses cached data, skipping compute()
        self.assertEqual(len(compute_calls), 2)

    def test_mis_report_back_button_tour(self):
        search_view = self.env.ref("account.view_account_move_line_filter")
        self.report_instance.write(
            {
                "widget_show_filters": True,
                "widget_search_view_id": search_view.id,
            }
        )
        action = self.env.ref("mis_builder.mis_report_instance_view_action")
        domain = f"[('id', '=', {self.report_instance.id})]"
        url = (
            f"/web#action={action.id}"
            f"&model=mis.report.instance"
            f"&view_type=list"
            f"&domain={domain}"
        )
        self.start_tour(url, "mis_report_back_button_tour", login="admin")

    def test_mis_report_back_button_no_filters_tour(self):
        self.report_instance.write(
            {
                "widget_show_filters": False,
                "widget_search_view_id": False,
            }
        )
        action = self.env.ref("mis_builder.mis_report_instance_view_action")
        domain = f"[('id', '=', {self.report_instance.id})]"
        url = (
            f"/web#action={action.id}"
            f"&model=mis.report.instance"
            f"&view_type=list"
            f"&domain={domain}"
        )
        self.start_tour(url, "mis_report_back_button_no_filters_tour", login="admin")
