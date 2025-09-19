# Copyright 2016 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.tools import test_reports

from odoo.addons.mis_builder.tests.test_mis_report_instance import TestMisReportInstance


class TestMisReportInstanceReportXlsx(TestMisReportInstance):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def test_xlsx(self):
        self.report_instance.export_xls()  # get action
        with self.assertLogs("odoo.tools.test_reports", level="WARNING") as log_catcher:
            test_reports.try_report(
                self.env.cr,
                self.env.uid,
                "mis_builder_report_xlsx.xls_export",
                [self.report_instance.id],
                report_type="xlsx",
            )
        self.assertIn(
            "Report mis_builder_report_xlsx.xls_export"
            ' produced a "xlsx" chunk, cannot examine it',
            log_catcher.output[0],
        )
