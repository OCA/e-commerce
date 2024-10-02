# Copyright (C) 2020 Alexandre Díaz - Tecnativa S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo.tools import config


def post_init_hook(env):
    if config["test_enable"] or config["test_file"]:
        env.ref("website_sale_require_login.cart").active = False
