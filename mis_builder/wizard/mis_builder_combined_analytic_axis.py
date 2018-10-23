# -*- coding: utf-8 -*-
# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import StringIO
import base64
import xlsxwriter

from odoo import api, fields, models

from ..models.accounting_none import AccountingNone
from ..models.data_error import DataError

HEADER_ROW_SHIFT = 1
BODY_ROW_SHIFT = 2
BODY_COL_SHIFT = 4
ROW_HEIGHT = 15  # xlsxwriter units
COL_WIDTH = 0.9  # xlsxwriter units
MIN_COL_WIDTH = 10  # characters
MAX_COL_WIDTH = 50  # characters

# TODO: improve xlsx style use
# TODO: hide empty columns?
# TODO: delete downloaded attachment?


class MisBuilderCombinedAnalyticAxis(models.TransientModel):
    _name = "mis.builder.combined.analytic.axis"

    @api.model
    def _default_company_id(self):
        default_company_id = self.env["res.company"]._company_default_get()
        return default_company_id

    template_id = fields.Many2one(
        comodel_name="mis.report", string="Template", required=True
    )

    date_from = fields.Date(string="Date From")
    date_to = fields.Date(string="Date To", default=fields.Date.today)
    account_analytic_id = fields.Many2one(
        comodel_name="account.analytic.account", string="Project"
    )
    include_account_analytic_children = fields.Boolean(
        string="Include Analytic Account children"
    )
    org_entity_id = fields.Many2one(
        comodel_name="hr.department",
        string="Organizational Entity",
        index=True,
    )
    include_org_entity_children = fields.Boolean(
        string="Include Organizational Entity children"
    )
    finance_source_id = fields.Many2one(
        comodel_name="finance.source", string="Finances Source"
    )
    include_finance_source_children = fields.Boolean(
        string="Include Finances Source children"
    )
    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
        default=_default_company_id,
        required=True,
    )

    @api.multi
    def get_cell_style(self, kpi_name):
        self.ensure_one()
        kpi = self.template_id.kpi_ids.filtered(lambda x: x.name == kpi_name)
        return kpi.style_id

    @api.multi
    def _get_xlsx_file_name(self):
        self.ensure_one()
        return "{template}, {date_from}-{date_to}".format(
            template=self.template_id.name,
            date_from=self.date_from,
            date_to=self.date_to,
        )

    @api.multi
    def _write_xlsx_body(self, workbook, worksheet, header, rows, data):
        """
        write xlsx report body based on evaluated data and pre-created xlsx
        header
        :param worksheet: xlsx worksheet object
        :param header: xlsx header
        :param data: evaluated data from combined mis report
        """
        self.ensure_one()
        style_obj = self.env["mis.report.style"]
        for combination in rows:
            for kpi_name in header:
                row_pos = rows.index(combination) + BODY_ROW_SHIFT
                col_pos = header.index(kpi_name) + BODY_COL_SHIFT
                val = data[combination][kpi_name]
                cell_xlsx_style = style_obj.to_xlsx_style(
                    self.get_cell_style(kpi_name)
                )
                cell_xlsx_style["align"] = "right"
                cell_format = workbook.add_format(cell_xlsx_style)
                if (
                    not val
                    or val is AccountingNone
                    or isinstance(val, DataError)
                ):
                    worksheet.write(row_pos, col_pos, "")
                    continue
                worksheet.write(row_pos, col_pos, val, cell_format)

    @api.multi
    def _write_xlsx_header(self, worksheet, data, header_format):
        """
        write xlsx report header based on evaluated data
        :param worksheet: xlsx worksheet object
        :param data: evaluated data from combined mis report
        :return: worksheet header index list
        """
        self.ensure_one()
        # FIXME: filter with instance != bound method
        header = filter(
            lambda x: isinstance(x, unicode), data.values()[0].keys()
        )
        for kpi_name in header:
            kpi = self.template_id.kpi_ids.filtered(
                lambda x: x.name == kpi_name
            )
            col_pos = header.index(kpi_name) + BODY_COL_SHIFT
            worksheet.write(
                HEADER_ROW_SHIFT, col_pos, kpi.description, header_format
            )
            col_width = min(MAX_COL_WIDTH, len(kpi.description))
            worksheet.set_column(col_pos, col_pos, col_width * COL_WIDTH)
        return header

    @api.multi
    def _write_xlsx_combination_section_body(self, worksheet, rows):
        """
        write xlsx left section based on possible combinations
        :param worksheet: xlsx worksheet object
        :param rows: all possible combination
        """
        for combination in rows:
            account_analytic_id, org_entity_id, finance_source_id = combination
            row_pos = rows.index(combination) + BODY_ROW_SHIFT
            worksheet.write(row_pos, 0, account_analytic_id.name)
            worksheet.write(
                row_pos,
                1,
                account_analytic_id.parent_id.name
                if account_analytic_id.parent_id
                else "",
            )
            worksheet.write(row_pos, 2, org_entity_id.name)
            worksheet.write(row_pos, 3, finance_source_id.name)
            worksheet.set_row(row_pos, ROW_HEIGHT)

    @api.multi
    def _write_xlsx_combination_section_header(self, worksheet, header_format):
        """
        write xlsx left section header based on model fields labels
        :param worksheet: xlsx worksheet object
        :return:
        """
        col_pos = 0
        current_model = self.env["ir.model"].search(
            [("model", "=", self._name)]
        )
        analytic_model = self.env["ir.model"].search(
            [("model", "=", "account.analytic.account")]
        )
        account_analytic_label = current_model.field_id.filtered(
            lambda x: x.name == "account_analytic_id"
        ).field_description
        worksheet.write(
            HEADER_ROW_SHIFT, col_pos, account_analytic_label, header_format
        )
        col_pos += 1
        account_analytic_parent_label = analytic_model.field_id.filtered(
            lambda x: x.name == "parent_id"
        ).field_description
        worksheet.write(
            HEADER_ROW_SHIFT,
            col_pos,
            account_analytic_parent_label,
            header_format,
        )
        col_pos += 1
        org_entity_label = current_model.field_id.filtered(
            lambda x: x.name == "org_entity_id"
        ).field_description
        worksheet.write(
            HEADER_ROW_SHIFT, col_pos, org_entity_label, header_format
        )
        col_pos += 1
        finance_source_label = current_model.field_id.filtered(
            lambda x: x.name == "finance_source_id"
        ).field_description
        worksheet.write(
            HEADER_ROW_SHIFT, col_pos, finance_source_label, header_format
        )

    @api.multi
    def _write_xlsx_combination_section(self, worksheet, data, header_format):
        """
        write xlsx left section
        :param worksheet: xlsx worksheet object
        :param data: evaluated data
        :return: worksheet rows index list
        """
        rows = data.keys()
        self._write_xlsx_combination_section_header(worksheet, header_format)
        self._write_xlsx_combination_section_body(worksheet, rows)
        return rows

    @api.multi
    def _write_xlsx(self, data):
        """
        write xlsx file
        :param data: evaluated data
        :return: StringIO object
        """
        self.ensure_one()
        output = StringIO.StringIO()
        workbook = xlsxwriter.Workbook(output)
        worksheet = workbook.add_worksheet()
        bold = workbook.add_format({"bold": True})
        worksheet.write(0, 0, self._get_xlsx_file_name(), bold)
        header_format = workbook.add_format(
            {"bold": True, "align": "center", "bg_color": "#F0EEEE"}
        )
        rows = self._write_xlsx_combination_section(
            worksheet, data, header_format
        )
        header = self._write_xlsx_header(worksheet, data, header_format)
        self._write_xlsx_body(workbook, worksheet, header, rows, data)
        return output

    @api.multi
    def get_possible_combination(self):
        """
        Get all possible combinations based on account move line
        :return: possible combinations
        """
        self.ensure_one()
        domain = [
            ("date", "<=", self.date_to),
            ("date", ">=", self.date_from),
            ("company_id", "=", self.company_id.id),
        ]
        if self.account_analytic_id:
            operator = (
                "child_of" if self.include_account_analytic_children else "="
            )
            domain.append(
                ("account_analytic_id", operator, self.account_analytic_id.id)
            )
        if self.org_entity_id:
            operator = "child_of" if self.include_org_entity_children else "="
            domain.append(("org_entity_id", operator, self.org_entity_id.id))
        if self.finance_source_id:
            operator = (
                "child_of" if self.include_finance_source_children else "="
            )
            domain.append(
                ("finance_source_id", operator, self.finance_source_id.id)
            )
        lines = self.env["account.move.line"].search(domain)
        possible_combinations = {}
        for line in lines:
            combination = (
                line.account_analytic_id,
                line.org_entity_id,
                line.finance_source_id,
            )
            if combination not in possible_combinations:
                possible_combinations[combination] = lambda: [
                    ("account_analytic_id", "=", line.account_analytic_id.id),
                    ("org_entity_id", "=", line.org_entity_id.id),
                    ("finance_source_id", "=", line.finance_source_id.id),
                ]

        return possible_combinations

    @api.multi
    def generate_xlsx_file(self):
        """
        evaluate all possible combinations of the given analytic axis.
        generate xlsx file and store it as an ir.attachment
        :return: xlsx file
        """
        self.ensure_one()
        possible_combinations = self.get_possible_combination()
        res = {}
        for combination in possible_combinations:
            aep = self.template_id._prepare_aep(self.company_id)
            template_evaluated = self.template_id.evaluate(
                aep,
                self.date_from,
                self.date_to,
                get_additional_move_line_filter=possible_combinations[
                    combination
                ],
            )
            res[combination] = template_evaluated
        output = self._write_xlsx(res)
        file_data = base64.encodestring(output.getvalue())
        attachment = self.env["ir.attachment"].create(
            {
                "name": self._get_xlsx_file_name(),
                "datas_fname": self._get_xlsx_file_name() + ".xlsx",
                "datas": file_data,
            }
        )
        return {
            "type": "ir.actions.report.xml",
            "report_type": "controller",
            "report_file": "/web/content/{attachment_id}?download=true".format(
                attachment_id=attachment.id
            ),
        }
