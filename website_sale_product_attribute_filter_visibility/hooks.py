# Copyright 2018 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, SUPERUSER_ID


def post_init_hook(cr, registry):
    # Publish in website all existing attributes after install this module.
    with api.Environment.manage():
        env = api.Environment(cr, SUPERUSER_ID, {})
        env['product.attribute'].search([]).write({
            'website_published': True,
        })
