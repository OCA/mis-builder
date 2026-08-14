# Copyright 2026 Ecosoft
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, models
from odoo.osv import expression


class IrActionsActWindow(models.Model):
    _inherit = "ir.actions.act_window"

    @api.model
    def _mis_builder_dashboard_domain(self):
        return [
            ("res_model", "=", "board.board"),
            ("view_id", "!=", False),
            "|",
            ("groups_id", "=", False),
            ("groups_id", "in", self.env.user._get_group_ids()),
        ]

    @api.model
    def name_search(self, name="", args=None, operator="ilike", limit=100):
        if not self.env.context.get("mis_builder_dashboard_selection"):
            return super().name_search(name, args, operator, limit)
        domain = expression.AND([self._mis_builder_dashboard_domain(), args or []])
        # Window actions are technical records that regular users cannot read.
        # Sudo only this selector and keep the available actions tightly scoped.
        return super(IrActionsActWindow, self.sudo()).name_search(
            name, domain, operator, limit
        )
