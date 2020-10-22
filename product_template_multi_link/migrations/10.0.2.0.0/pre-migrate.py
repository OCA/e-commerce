# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade
import logging
import odoo

__name__ = "Upgrade to 10.0.2.0.0: Add product template link and optimizations"

_logger = logging.getLogger(__name__)


def _remove_circular(cr, env):
    # Remove circular links
    query = """
        DELETE FROM product_template_link
        WHERE product_template_id = linked_product_template_id
    """
    cr.execute(query)


def _remove_triplets(cr, env):
    """
    If there are several links with same triplet
    (product_template_id, linked_product_template_id, link_type),
    we remove the duplicates
    """
    query = """
        WITH links AS (
            SELECT
                id,
                product_template_id,
                linked_product_template_id,
                link_type,
                ROW_NUMBER() OVER (
                    PARTITION BY
                        product_template_id,
                        linked_product_template_id,
                        link_type
                    ORDER BY
                        product_template_id,
                        linked_product_template_id,
                        link_type
                ) row_num
            FROM
                product_template_link
            )
            DELETE FROM product_template_link ptl WHERE EXISTS
            (SELECT 1 FROM links WHERE row_num > 1 AND id = ptl.id);
    """
    cr.execute(query)


def _add_fields(cr, env):
    if not openupgrade.column_exists(
            cr, "product_template_link", "left_product_tmpl_id"):
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
            WHERE left_product_tmpl_id IS NULL
            AND right_product_tmpl_id IS NULL
    """
    cr.execute(query)


def migrate(cr, version):

    with odoo.api.Environment.manage():
        env = odoo.api.Environment(cr, odoo.SUPERUSER_ID, {})

        _remove_circular(cr, env)
        _remove_triplets(cr, env)
        _add_fields(cr, env)
        _populate_fields(cr, env)
