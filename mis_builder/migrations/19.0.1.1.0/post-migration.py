# Copyright 2026 Odoo Community Association (OCA)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).


def migrate(cr, version):
    """Map legacy auto_expand_accounts onto detail_by."""
    cr.execute(
        """
        UPDATE mis_report_kpi
           SET detail_by = 'account'
         WHERE auto_expand_accounts IS TRUE
           AND (detail_by IS NULL OR detail_by = 'none')
        """
    )
