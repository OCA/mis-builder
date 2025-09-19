# Copyright 2016 Therp BV (<http://therp.nl>)
# Copyright 2016 ACSONE SA/NV (<http://acsone.eu>)
# Copyright 2020 CorporateHub (https://corporatehub.eu)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, models

from odoo.addons.mis_builder.models.mis_report_style import TYPE_NUM, TYPE_PCT


class MisReportStyle(models.Model):
    _inherit = "mis.report.style"

    _font_size_to_xlsx_size = {
        "medium": 11,
        "xx-small": 5,
        "x-small": 7,
        "small": 9,
        "large": 13,
        "x-large": 15,
        "xx-large": 17,
    }

    @api.model
    def to_xlsx_style(self, var_type, props, no_indent=False):
        xlsx_attributes = [
            ("italic", props.font_style == "italic"),
            ("bold", props.font_weight == "bold"),
            ("font_size", self._font_size_to_xlsx_size.get(props.font_size, 11)),
            ("font_color", props.color),
            ("bg_color", props.background_color),
        ]
        if var_type == TYPE_NUM:
            num_format = "#,##0"
            if props.dp:
                num_format += "."
                num_format += "0" * props.dp
            if props.prefix:
                num_format = f'"{props.prefix} "{num_format}'
            if props.suffix:
                num_format = f'{num_format}" {props.suffix}"'
            xlsx_attributes.append(("num_format", num_format))
        elif var_type == TYPE_PCT:
            num_format = "0"
            if props.dp:
                num_format += "."
                num_format += "0" * props.dp
            num_format += "%"
            xlsx_attributes.append(("num_format", num_format))
        if props.indent_level is not None and not no_indent:
            xlsx_attributes.append(("indent", props.indent_level))
        return dict([a for a in xlsx_attributes if a[1] is not None])
