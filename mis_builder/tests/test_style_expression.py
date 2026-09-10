# Copyright 2026 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase

from odoo.addons.mis_builder.models.expression_evaluator import ExpressionEvaluator

KPIMATRIX_LOGGER = "odoo.addons.mis_builder.models.kpimatrix"


class TestStyleExpression(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env["mis.report.style"].create(
            dict(name="Big", color_inherit=False, color="#00FF00")
        )
        cls.report = cls.env["mis.report"].create(dict(name="test style expression"))
        # k1 depends on k2, which is computed after it, so k1 is evaluated a
        # first time with an incomplete locals_dict, requeued, then evaluated
        # again in a second pass.
        cls.k1 = cls.env["mis.report.kpi"].create(
            dict(
                report_id=cls.report.id,
                name="k1",
                description="kpi 1",
                sequence=1,
                expression="k2 + 1",
                style_expression="'Big' if k1 > 10 else 'Small'",
            )
        )
        cls.k2 = cls.env["mis.report.kpi"].create(
            dict(
                report_id=cls.report.id,
                name="k2",
                description="kpi 2",
                sequence=2,
                expression="20",
            )
        )

    def _compute(self):
        kpi_matrix = self.report.prepare_kpi_matrix()
        self.report._declare_and_compute_col(
            ExpressionEvaluator(aep=None, date_from="2017-01-01", date_to="2017-01-31"),
            kpi_matrix,
            "col1",
            "col 1",
            None,
            None,
            {},
        )
        return kpi_matrix

    def _cells(self, kpi_matrix, kpi_name):
        for row in kpi_matrix.iter_rows():
            if row.kpi.name == kpi_name:
                return [cell for cell in row.iter_cells() if cell is not None]
        raise AssertionError(f"no row for kpi {kpi_name}")

    def test_style_expression_of_requeued_kpi(self):
        """The style of a requeued kpi comes from its last evaluation.

        The intermediate passes must not be reported, as an unresolvable
        style is expected while locals_dict is still incomplete.
        """
        with self.assertNoLogs(KPIMATRIX_LOGGER, level="ERROR"):
            kpi_matrix = self._compute()
        cells = self._cells(kpi_matrix, "k1")
        self.assertEqual([cell.val for cell in cells], [21])
        self.assertEqual(cells[0].style_props["color"], "#00FF00")

    def test_style_expression_error(self):
        """A style expression that cannot be evaluated is reported."""
        self.k1.style_expression = "'Big' if unknown_kpi > 10 else 'Small'"
        with self.assertLogs(KPIMATRIX_LOGGER, level="ERROR") as log:
            kpi_matrix = self._compute()
        self.assertEqual([cell.val for cell in self._cells(kpi_matrix, "k1")], [21])
        self.assertEqual(len(log.output), 1)
        self.assertIn("Error evaluating style expression", log.output[0])
        self.assertIn("unknown_kpi", log.output[0])

    def test_style_expression_not_found(self):
        """A style expression naming an unknown style is reported."""
        self.k1.style_expression = "'No Such Style'"
        with self.assertLogs(KPIMATRIX_LOGGER, level="ERROR") as log:
            self._compute()
        self.assertEqual(len(log.output), 1)
        self.assertIn("Style 'No Such Style' not found.", log.output[0])
