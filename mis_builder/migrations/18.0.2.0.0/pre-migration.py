import logging

from openupgradelib import openupgrade

_logger = logging.getLogger(__name__)

xmlid_renames = [
    ("mis_builder.xls_export", "mis_builder_report_xlsx.xls_export"),
]


@openupgrade.migrate()
def migrate(env, version):
    env.cr.execute("""
        SELECT count(*)
        FROM ir_module_module
        WHERE name = 'mis_builder_report_xlsx'""")
    if env.cr.fetchone()[0] == 0:
        _logger.error(
            "Unable to found the module mis_builder_report_xlsx.\n"
            " The module mis_builder has been refactored"
            " and splitted into another module named"
            " 'mis_builder_report_xlsx'."
            " If you don't get this module in your addons path"
            " the feature to export in XLSX will be lost.\n"
            " More information:"
            " https://github.com/OCA/mis-builder/pull/728"
        )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE ir_module_module
        SET state='to upgrade'
        WHERE name = 'mis_builder_report_xlsx' AND state='uninstalled'""",
    )
    openupgrade.rename_xmlids(env.cr, xmlid_renames)
