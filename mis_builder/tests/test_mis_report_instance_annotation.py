# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import Command
from odoo.tests.common import TransactionCase


class TestMisReportInstanceAnnotation(TransactionCase):
    def setUp(self):
        super().setUp()
        self.report = self.env["mis.report"].create(
            {
                "name": "test report",
                "subkpi_ids": [
                    Command.create(
                        {
                            "name": "subkpi1_report2",
                            "description": "subkpi 1, report 2",
                            "sequence": 1,
                        }
                    ),
                    Command.create(
                        {
                            "name": "subkpi2_report2",
                            "description": "subkpi 2, report 2",
                            "sequence": 2,
                        },
                    ),
                ],
            }
        )

        self.kpi = self.env["mis.report.kpi"].create(
            {
                "report_id": self.report.id,
                "description": "kpi 1",
                "name": "k1",
                "multi": True,
                "expression_ids": [
                    Command.create(
                        {
                            "name": "bale[200%]",
                            "subkpi_id": self.report.subkpi_ids[0].id,
                        },
                    ),
                    Command.create(
                        {
                            "name": "balp[200%]",
                            "subkpi_id": self.report.subkpi_ids[1].id,
                        },
                    ),
                ],
            }
        )

        self.report_instance = self.env["mis.report.instance"].create(
            {
                "name": "test instance",
                "report_id": self.report.id,
                "company_id": self.env.ref("base.main_company").id,
                "period_ids": [
                    Command.create(
                        {
                            "name": "p1",
                            "mode": "fix",
                            "manual_date_from": "2013-01-01",
                            "manual_date_to": "2013-12-31",
                            "sequence": 1,
                        },
                    ),
                    Command.create(
                        {
                            "name": "p2",
                            "mode": "fix",
                            "manual_date_from": "2014-01-01",
                            "manual_date_to": "2014-12-31",
                            "sequence": 2,
                        },
                    ),
                ],
            }
        )

    def test_adding_note(self):
        notes = self.report_instance.get_notes_by_cell_id()

        self.assertEqual({}, notes)

        # report with 4 cells, 2 periods and 2 subkpis
        matrix = self.report_instance._compute_matrix()
        cell_ids = [c.cell_id for row in matrix.iter_rows() for c in row.iter_cells()]
        self.assertEqual(len(cell_ids), 4)

        first_cell_id, second_cell_id, third_cell_id, _fourth_cell_id = cell_ids

        # adding one note
        self.env["mis.report.instance.annotation"].set_annotation(
            first_cell_id, self.report_instance.id, "This is a note"
        )
        notes = self.report_instance.get_notes_by_cell_id()
        self.assertDictEqual(
            {first_cell_id: {"text": "This is a note", "sequence": 1}}, notes
        )

        # adding another note
        self.env["mis.report.instance.annotation"].set_annotation(
            third_cell_id, self.report_instance.id, "This is another note"
        )
        notes = self.report_instance.get_notes_by_cell_id()
        self.assertDictEqual(
            {
                first_cell_id: {"text": "This is a note", "sequence": 1},
                third_cell_id: {"text": "This is another note", "sequence": 2},
            },
            notes,
        )

        self.env["mis.report.instance.annotation"].set_annotation(
            second_cell_id, self.report_instance.id, "This is third note"
        )

        notes = self.report_instance.get_notes_by_cell_id()
        # Last note added should have a sequence of
        # 2 since it is deplayed in the second cell
        self.assertDictEqual(
            {
                first_cell_id: {"text": "This is a note", "sequence": 1},
                second_cell_id: {"text": "This is third note", "sequence": 2},
                third_cell_id: {"text": "This is another note", "sequence": 3},
            },
            notes,
        )

    def test_remove_note(self):
        notes = self.report_instance.get_notes_by_cell_id()

        self.assertEqual({}, notes)

        # report with 4 cells, 2 periods and 2 subkpis
        matrix = self.report_instance._compute_matrix()
        cell_ids = [c.cell_id for row in matrix.iter_rows() for c in row.iter_cells()]
        self.assertEqual(len(cell_ids), 4)

        first_cell_id = cell_ids[0]

        # adding one note
        self.env["mis.report.instance.annotation"].set_annotation(
            first_cell_id, self.report_instance.id, "This is a note"
        )
        notes = self.report_instance.get_notes_by_cell_id()
        self.assertDictEqual(
            {first_cell_id: {"text": "This is a note", "sequence": 1}}, notes
        )

        # remove note
        self.env["mis.report.instance.annotation"].remove_annotation(
            first_cell_id, self.report_instance.id
        )
        notes = self.report_instance.get_notes_by_cell_id()
        self.assertEqual({}, notes)
