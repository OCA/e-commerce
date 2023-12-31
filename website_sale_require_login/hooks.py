# Copyright (C) 2020 Alexandre Díaz - Tecnativa S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import SUPERUSER_ID, api
from odoo.tools import config


def post_init_hook(cr, registry):
    if config["test_enable"] or config["test_file"]:
        with api.Environment.manage():
            env = api.Environment(cr, SUPERUSER_ID, {})
            env.ref("website_sale_require_login.cart").active = False
            env.ref("website_sale_require_login.short_cart_summary").active = False
