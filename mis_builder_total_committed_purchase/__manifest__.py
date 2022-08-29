# Copyright 2017-2018 ACSONE SA/NV
# Copyright 2022 Camptocamp SA (https://www.camptocamp.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "MIS Builder Total Committed Purchase",
    "summary": """Addon to create a alternative source based on all purchase order line with
    MIS Builder.""",
    "version": "15.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV, Camptocamp, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/mis-builder",
    "depends": ["mis_builder", "purchase"],
    "data": [
        "data/mis_total_committed_purchase.sql",
        "data/mis_total_committed_purchase_tag_rel.sql",
        "security/mis_total_committed_purchase.xml",
        "views/mis_total_committed_purchase.xml",
    ],
    "installable": True,
}
