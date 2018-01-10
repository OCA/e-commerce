# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, SUPERUSER_ID
from odoo.exceptions import UserError


def _add_trgm_index_product_tmpl_name(cr, registry):
    with cr.savepoint():
        env = api.Environment(cr, SUPERUSER_ID, {})
        trgm_mod = env['trgm.index']

        if trgm_mod._trgm_extension_exists() != 'installed':
            raise UserError(_(
                'TRGM extension has not been installed on your database. '
                'Follow the config instructions from base_search_fuzzy before '
                'installing this module.'
            ))

        if not trgm_mod.index_exists('product.template', 'name'):
            field_tmpl_name = env.ref('product.field_product_template_name')
            trgm_mod.create({
                'field_id': field_tmpl_name.id,
                'index_type': 'gin',
            })
