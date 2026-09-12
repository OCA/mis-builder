# Copyright 2026 Odoo Community Association (OCA)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).


def migrate(cr, version):
    """Map legacy detail expansion flags onto detail_groupby."""
    cr.execute(
        """
        SELECT column_name
          FROM information_schema.columns
         WHERE table_name = 'mis_report_kpi'
           AND column_name IN ('detail_by', 'detail_groupby', 'auto_expand_accounts')
        """
    )
    columns = {row[0] for row in cr.fetchall()}
    if "detail_groupby" not in columns:
        return

    if "detail_by" in columns:
        cr.execute(
            """
            UPDATE mis_report_kpi
               SET detail_groupby = CASE
                    WHEN detail_by = 'account' THEN 'account_id'
                    WHEN detail_by = 'partner' THEN 'partner_id'
                    WHEN auto_expand_accounts IS TRUE THEN 'account_id'
                    ELSE detail_groupby
               END
             WHERE detail_groupby IS NULL
                OR detail_groupby = ''
            """
        )
    else:
        cr.execute(
            """
            UPDATE mis_report_kpi
               SET detail_groupby = 'account_id'
             WHERE auto_expand_accounts IS TRUE
               AND (detail_groupby IS NULL OR detail_groupby = '')
            """
        )
