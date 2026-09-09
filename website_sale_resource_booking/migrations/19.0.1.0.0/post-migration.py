# Copyright 2026 Tecnativa - Pilar Vargas
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from openupgradelib import openupgrade

from odoo.addons.website_sale_resource_booking import post_init_hook


@openupgrade.migrate()
def migrate(env, version):
    post_init_hook(env)
