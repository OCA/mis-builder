# Copyright 2014 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import logging
import numbers
from collections import defaultdict
from datetime import datetime

from odoo import api, fields, models

from ..models.accounting_none import AccountingNone
from ..models.data_error import DataError
from ..models.mis_report_style import TYPE_STR

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

    def _write_report_title(self, workbook, sheet, row_pos, report_name):
        bold = workbook.add_format({"bold": True})
        sheet.write(row_pos, 0, report_name, bold)
        row_pos += 2
        return row_pos

    def _write_filters(self, sheet, row_pos, objects):
        filter_descriptions = objects.get_filter_descriptions()
        if filter_descriptions:
            for filter_description in objects.get_filter_descriptions():
                sheet.write(row_pos, 0, filter_description)
                row_pos += 1
            row_pos += 1
        return row_pos

    def _write_col_headers(self, workbook, sheet, row_pos, matrix, col_width):
        header_format = workbook.add_format(
            {"bold": True, "align": "center", "bg_color": "#F0EEEE"}
        )
        sheet.write(row_pos, 0, "", header_format)
        col_pos = 1
        for col in matrix.iter_cols():
            label = col.label
            if col.description:
                label += "\n" + col.description
                sheet.set_row(row_pos, ROW_HEIGHT * 2)
            if col.colspan > 1:
                sheet.merge_range(
                    row_pos,
                    col_pos,
                    row_pos,
                    col_pos + col.colspan - 1,
                    label,
                    header_format,
                )
            else:
                sheet.write(row_pos, col_pos, label, header_format)
                col_width[col_pos] = max(
                    col_width[col_pos], len(col.label or ""), len(col.description or "")
                )
            col_pos += col.colspan
        sheet.write(row_pos, col_pos, "Annotations", header_format)
        row_pos += 1
        return row_pos, col_width

    def _write_subcol_headers(self, workbook, sheet, row_pos, matrix, col_width):
        header_format = workbook.add_format(
            {"bold": True, "align": "center", "bg_color": "#F0EEEE"}
        )
        sheet.write(row_pos, 0, "", header_format)
        col_pos = 1
        for subcol in matrix.iter_subcols():
            label = subcol.label
            if subcol.description:
                label += "\n" + subcol.description
                sheet.set_row(row_pos, ROW_HEIGHT * 2)
            sheet.write(row_pos, col_pos, label, header_format)
            col_width[col_pos] = max(
                col_width[col_pos],
                len(subcol.label or ""),
                len(subcol.description or ""),
            )
            col_pos += 1
        row_pos += 1
        return row_pos, col_width

    def _write_rows(
        self,
        workbook,
        sheet,
        row_pos,
        matrix,
        notes,
        style_obj,
        label_col_width,
        col_width,
    ):
        for row in matrix.iter_rows():
            if (
                row.style_props.hide_empty and row.is_empty()
            ) or row.style_props.hide_always:
                continue
            row_xlsx_style = style_obj.to_xlsx_style(TYPE_STR, row.style_props)
            row_format = workbook.add_format(row_xlsx_style)
            col_pos = 0
            label = row.label
            if row.description:
                label += "\n" + row.description
                sheet.set_row(row_pos, ROW_HEIGHT * 2)
            sheet.write(row_pos, col_pos, label, row_format)
            label_col_width = max(
                label_col_width, len(row.label or ""), len(row.description or "")
            )
            for cell in row.iter_cells():
                col_pos += 1
                self._mis_builder_add_annotation(sheet, cell, row_pos, col_pos, notes)
                if not cell or cell.val is AccountingNone:
                    # TODO col/subcol format
                    sheet.write(row_pos, col_pos, "", row_format)
                    continue
                cell_xlsx_style = style_obj.to_xlsx_style(
                    cell.val_type, cell.style_props, no_indent=True
                )
                cell_xlsx_style["align"] = "right"
                cell_format = workbook.add_format(cell_xlsx_style)
                if isinstance(cell.val, DataError):
                    val = cell.val.name
                    # TODO display cell.val.msg as Excel comment?
                elif cell.val is None or cell.val is AccountingNone:
                    val = ""
                else:
                    divider = float(cell.style_props.get("divider", 1))
                    if (
                        divider != 1
                        and isinstance(cell.val, numbers.Number)
                        and not cell.val_type == "pct"
                    ):
                        val = cell.val / divider
                    else:
                        val = cell.val
                sheet.write(row_pos, col_pos, val, cell_format)
                col_width[col_pos] = max(
                    col_width[col_pos], len(cell.val_rendered or "")
                )
            first_cell = next(row.iter_cells(), None)
            if first_cell:
                annotation = notes.get(first_cell.cell_id, {}).get("text")
                if annotation:
                    sheet.write(row_pos, col_pos + 1, annotation, row_format)
            row_pos += 1
        return row_pos, label_col_width, col_width

    def _write_footer(self, workbook, sheet, row_pos):
        row_pos += 1
        footer_format = workbook.add_format(
            {"italic": True, "font_color": "#202020", "font_size": 9}
        )
        lang_model = self.env["res.lang"]
        lang = lang_model._lang_get(self.env.user.lang)

        now_tz = fields.Datetime.context_timestamp(
            self.env["res.users"], datetime.now()
        )
        create_date = self.env._(
            "Generated on %(gen_date)s at %(gen_time)s",
            gen_date=now_tz.strftime(lang.date_format),
            gen_time=now_tz.strftime(lang.time_format),
        )
        sheet.write(row_pos, 0, create_date, footer_format)

    def _adjust_col_widths(self, sheet, label_col_width, col_width):
        sheet.set_column(0, 0, min(label_col_width, MAX_COL_WIDTH) * COL_WIDTH)
        data_col_width = min(MAX_COL_WIDTH, max(col_width.values()))
        min_col_pos = min(col_width.keys())
        max_col_pos = max(col_width.keys())
        sheet.set_column(min_col_pos, max_col_pos, data_col_width * COL_WIDTH)
