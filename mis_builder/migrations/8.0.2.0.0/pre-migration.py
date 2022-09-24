# Copyright 2021 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    old_column = "auto_expand_accounts"
    new_column = "auto_expand"

    if not openupgrade.column_exists(env.cr, "mis_report", new_column):
        openupgrade.rename_fields(
            env,
            [
                (
                    "mis.report",
                    "mis_report",
                    old_column,
                    new_column,
                ),
            ],
        )
    
    old_column = "auto_expand_accounts_style_id"
    new_column = "auto_expand_style_id"

    if not openupgrade.column_exists(env.cr, "mis_report", new_column):
        openupgrade.rename_fields(
            env,
            [
                (
                    "mis.report",
                    "mis_report",
                    old_column,
                    new_column,
                ),
            ],
        )
