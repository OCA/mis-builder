from . import models


def uninstall_hook(cr, registry):
    # drop relation view manually because Odoo does not know about it
    cr.execute("DROP VIEW IF EXISTS mis_committed_purchase_tag_rel")
