# Copyright 2021 Tecnativa - Pedro M. Baeza
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
from odoo import SUPERUSER_ID, api


def migrate(cr, version):
    """Remove offending view for allowing to update."""
    env = api.Environment(cr, SUPERUSER_ID, {})
    view = env.ref("website_sale_product_attachment.download_icons", False)
    if view:
        view.unlink()
