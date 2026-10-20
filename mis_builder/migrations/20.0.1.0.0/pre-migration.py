# Copyright 2026 KMEE
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).


def migrate(cr, version):
    # ir.model.access and ir.rule were replaced by ir.access: drop the xmlids
    # still pointing to the legacy models so that ir.access.csv can load
    cr.execute(
        """
        DELETE FROM ir_model_data
        WHERE module = 'mis_builder'
          AND model IN ('ir.model.access', 'ir.rule')
        """
    )
