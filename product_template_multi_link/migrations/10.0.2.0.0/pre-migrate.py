# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade
import logging
import odoo

__name__ = "Upgrade to 10.0.2.0.0: Add product template link and optimizations"

_logger = logging.getLogger(__name__)


def _add_fields(cr, env):
    fields = [
        ('left_product_tmpl_id', 'product.template.link',
         'product_template_link', 'many2one', 'integer',
         'product_template_multi_link'),
        ('right_product_tmpl_id', 'product.template.link',
         'product_template_link', 'many2one', 'integer',
         'product_template_multi_link'),
    ]
    openupgrade.add_fields(env, fields)


def _populate_fields(cr, env):
    query = """
        UPDATE product_template_link
        SET left_product_tmpl_id = product_template_id,
            right_product_tmpl_id = linked_product_template_id
    """
    cr.execute(query)


def migrate(cr, version):

    with odoo.api.Environment.manage():
        env = odoo.api.Environment(cr, odoo.SUPERUSER_ID, {})

        _add_fields(cr, env)
        _populate_fields(cr, env)
