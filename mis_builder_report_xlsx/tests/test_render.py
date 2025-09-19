# Copyright 2016 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).


from odoo.addons.mis_builder.models.mis_report_style import TYPE_NUM, TYPE_PCT, TYPE_STR
from odoo.addons.mis_builder.tests.test_render import TestRendering


class TestRenderingReportXlsx(TestRendering):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def test_xlsx(self):
        self.style.color_inherit = False
        self.style.color = "#FF0000"
        self.style.background_color_inherit = False
        self.style.background_color = "#0000FF"
        self.style.suffix_inherit = False
        self.style.suffix = "s"
        self.style.prefix_inherit = False
        self.style.prefix = "p"
        self.style.dp_inherit = False
        self.style.dp = 2
        self.style.font_style_inherit = False
        self.style.font_style = "italic"
        self.style.font_weight_inherit = False
        self.style.font_weight = "bold"
        self.style.font_size_inherit = False
        self.style.font_size = "small"
        self.style.indent_level_inherit = False
        self.style.indent_level = 2
        style_props = self.style_obj.merge([self.style])
        xlsx = self.style_obj.to_xlsx_style(TYPE_NUM, style_props)
        self.assertEqual(
            xlsx,
            {
                "italic": True,
                "bold": True,
                "font_size": 9,
                "font_color": "#FF0000",
                "bg_color": "#0000FF",
                "num_format": '"p "#,##0.00" s"',
                "indent": 2,
            },
        )
        xlsx = self.style_obj.to_xlsx_style(TYPE_NUM, style_props, no_indent=True)
        self.assertEqual(
            xlsx,
            {
                "italic": True,
                "bold": True,
                "font_size": 9,
                "font_color": "#FF0000",
                "bg_color": "#0000FF",
                "num_format": '"p "#,##0.00" s"',
            },
        )
        # percent type ignore prefix and suffix
        xlsx = self.style_obj.to_xlsx_style(TYPE_PCT, style_props, no_indent=True)
        self.assertEqual(
            xlsx,
            {
                "italic": True,
                "bold": True,
                "font_size": 9,
                "font_color": "#FF0000",
                "bg_color": "#0000FF",
                "num_format": "0.00%",
            },
        )

        # str type have no num_format style
        xlsx = self.style_obj.to_xlsx_style(TYPE_STR, style_props, no_indent=True)
        self.assertEqual(
            xlsx,
            {
                "italic": True,
                "bold": True,
                "font_size": 9,
                "font_color": "#FF0000",
                "bg_color": "#0000FF",
            },
        )
