# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).


def migrate(cr, version):
    # Let the CSV recreate the external ID if it still points to the old model.
    cr.execute(
        """
        DELETE FROM ir_model_data
        WHERE module = 'mis_builder_demo'
          AND name = 'mis_committed_purchase_access_name'
          AND model = 'ir.model.access'
        """
    )
