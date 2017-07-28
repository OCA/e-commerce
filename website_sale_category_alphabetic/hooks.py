# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, SUPERUSER_ID


def post_init_hook_categorize_existing_products(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    env['product.template'].search([])._add_alpha_website_categ()
