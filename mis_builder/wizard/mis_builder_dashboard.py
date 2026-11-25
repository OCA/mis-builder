# Copyright 2014 ACSONE SA/NV (<http://acsone.eu>)
# Copyright 2020 CorporateHub (https://corporatehub.eu)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from lxml import etree

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class AddMisReportInstanceDashboard(models.TransientModel):
    _name = "add.mis.report.instance.dashboard.wizard"
    _description = "MIS Report Add to Dashboard Wizard"

    name = fields.Char(required=True)

    dashboard_id = fields.Many2one(
        comodel_name="ir.actions.act_window",
        required=True,
        domain="[('res_model', '=', 'board.board')]",
        context={"mis_builder_dashboard_selection": True},
        default=lambda self: self._default_dashboard_id(),
    )

    @api.model
    def _dashboard_domain(self):
        return self.env["ir.actions.act_window"]._mis_builder_dashboard_domain()

    @api.model
    def _default_dashboard_id(self):
        dashboard = self.env.ref("board.open_board_my_dash_action", False)
        if dashboard and dashboard.sudo().filtered_domain(self._dashboard_domain()):
            return dashboard.id
        return False

    def _get_dashboard(self):
        self.ensure_one()
        dashboard_id = self.sudo().dashboard_id.id
        dashboard = (
            self.env["ir.actions.act_window"]
            .sudo()
            .search(
                [("id", "=", dashboard_id), *self._dashboard_domain()],
                limit=1,
            )
        )
        if not dashboard:
            raise ValidationError(
                self.env._("The selected dashboard is not available to your user.")
            )
        return dashboard

    @api.model
    def default_get(self, fields_list):
        res = {}
        if self.env.context.get("active_id", False):
            res = super().default_get(fields_list)
            # get report instance name
            res["name"] = (
                self.env["mis.report.instance"]
                .browse(self.env.context["active_id"])
                .name
            )
        return res

    def action_add_to_dashboard(self):
        active_model = self.env.context.get("active_model")
        assert active_model == "mis.report.instance"
        active_id = self.env.context.get("active_id")
        assert active_id
        dashboard = self._get_dashboard()
        # create the act_window corresponding to this report
        self.env.ref("mis_builder.mis_report_instance_result_view_form")
        view = self.env.ref("mis_builder.mis_report_instance_result_view_form")
        report_result = (
            self.env["ir.actions.act_window"]
            .sudo()
            .create(
                {
                    "name": f"mis.report.instance.result.view.action."
                    f"{self.env.context['active_id']}",
                    "res_model": active_model,
                    "res_id": active_id,
                    "target": "current",
                    "view_mode": "form",
                    "view_id": view.id,
                    "context": self.env.context,
                }
            )
        )
        # add this result in the selected dashboard
        custom_views = self.env["ir.ui.view.custom"].sudo()
        last_customization = custom_views.search(
            [
                ("user_id", "=", self.env.uid),
                ("ref_id", "=", dashboard.view_id.id),
            ],
            limit=1,
        )
        arch = dashboard.view_id.arch
        if last_customization:
            arch = last_customization[0].arch
        new_arch = etree.fromstring(arch)
        column = new_arch.xpath("//column")[0]
        # Due to native dashboard doesn't support form view
        # add "from_dashboard" to context to get correct views in "get_views"
        context = dict(self.env.context, from_dashboard=True)
        column.append(
            etree.Element(
                "action",
                {
                    "context": str(context),
                    "name": str(report_result.id),
                    "string": self.name,
                    "view_mode": "form",
                },
            )
        )
        custom_views.create(
            {
                "user_id": self.env.uid,
                "ref_id": dashboard.view_id.id,
                "arch": etree.tostring(new_arch, pretty_print=True),
            }
        )

        return {"type": "ir.actions.act_window_close"}
