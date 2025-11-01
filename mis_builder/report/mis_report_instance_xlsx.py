# Copyright 2014 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import logging
from collections import defaultdict

from odoo import api, models

_logger = logging.getLogger(__name__)


ROW_HEIGHT = 15  # xlsxwriter units
COL_WIDTH = 0.9  # xlsxwriter units
MIN_COL_WIDTH = 10  # characters
MAX_COL_WIDTH = 50  # characters


class MisBuilderXlsx(models.AbstractModel):
    _name = "report.mis_builder.mis_report_instance_xlsx"
    _description = "MIS Builder XLSX report"
    _inherit = "report.report_xlsx.abstract"

    @api.model
    def _mis_builder_add_annotation(self, sheet, cell, row_pos, col_pos, notes):
        """
        Add anotation as a comment on cell in .xls
        """
        if cell and (annotation := notes.get(cell.cell_id, {}).get("text")):
            sheet.write_comment(row_pos, col_pos, annotation)

    def generate_xlsx_report(self, workbook, data, objects):
        # get the computed result of the report
        matrix = objects._compute_matrix()
        notes = objects.get_notes_by_cell_id()
        style_obj = self.env["mis.report.style"]

        # create worksheet
        report_name = "{} - {}".format(
            objects[0].name, ", ".join([a.name for a in objects[0].query_company_ids])
        )
        sheet = workbook.add_worksheet(report_name[:31])
        row_pos = 0
        # width of the labels column
        label_col_width = MIN_COL_WIDTH
        # {col_pos: max width in characters}
        col_width = defaultdict(lambda: MIN_COL_WIDTH)

        row_pos = self._write_report_title(workbook, sheet, row_pos, report_name)

        row_pos = self._write_filters(sheet, row_pos, objects)

        row_pos, col_width = self._write_col_headers(
            workbook, sheet, row_pos, matrix, col_width
        )

        row_pos, col_width = self._write_subcol_headers(
            workbook, sheet, row_pos, matrix, col_width
        )

        row_pos, label_col_width, col_width = self._write_rows(
            workbook,
            sheet,
            row_pos,
            matrix,
            notes,
            style_obj,
            label_col_width,
            col_width,
        )

        self._write_footer(workbook, sheet, row_pos)

        self._adjust_col_widths(sheet, label_col_width, col_width)
