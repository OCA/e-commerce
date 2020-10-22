# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from collections import defaultdict
from openupgradelib import openupgrade
import logging
import odoo

__name__ = "Upgrade to 10.0.2.0.0: Add product template link and optimizations"

_logger = logging.getLogger(__name__)


def _remove_duplicates(cr, env):
    """
    As the former implementation allows to create several links for
    bi-directionnal, we need to remove duplicate ones as the current
    implementation makes links bi-directional automatically.

    Remove former demo data records
    """
    ids = []
    ids.append("product_template_multi_link.link_apple_1")
    ids.append("product_template_multi_link.link_apple_2")
    ids.append("product_template_multi_link.link_membership_1")
    ids.append("product_template_multi_link.link_membership_2")
    ids.append("product_template_multi_link.link_membership_3")
    openupgrade.delete_records_safely_by_xml_id(env, ids)

    link_obj = env["product.template.link"]

    # former fields are not in registry
    query = """
        SELECT id, product_template_id, linked_product_template_id, link_type
        FROM product_template_link
    """
    cr.execute(query)
    lines = cr.fetchall()
    ids = []
    for line in lines:
        ids.append(line[0])
    records = link_obj.browse(ids)
    records.mapped("left_product_tmpl_id")
    records.mapped("right_product_tmpl_id")

    links_by_type = {}
    duplicates = []
    # Take the former link_type from DB directly as field is removed
    # but browse records in order to avoid inconsistencies
    for line in lines:
        record = records.browse(line[0])
        if line[3] not in links_by_type:
            links_by_type[line[3]] = {}
        if record.right_product_tmpl_id.id in links_by_type[line[3]] and\
                record.left_product_tmpl_id.id in \
                links_by_type[line[3]][record.right_product_tmpl_id.id]:
            duplicates.append(record.id)
        if record.left_product_tmpl_id.id not in links_by_type[line[3]]:
            links_by_type[line[3]][line[1]] = [line[2]]
        else:
            links_by_type[line[3]][line[1]].append(line[2])

    link_obj.browse(duplicates).unlink()


def _set_link_types(cr, env):
    openupgrade.load_data(
        cr,
        "product_template_multi_link",
        "data/product_template_link_type.xml")
    mapping = {
        "cross_sell": "cross-selling",
        "up_sell": "up-selling",
    }
    link_obj = env["product.template.link"]
    query = """
         SELECT id, link_type FROM product_template_link WHERE type_id IS NULL
    """
    cr.execute(query)
    product_links = defaultdict(list)

    for row in cr.fetchall():
        if row[1] in mapping:
            product_links[mapping[row[1]]].append(row[0])

    link_types = env["product.template.link.type"].search([])
    for link_type in link_types:
        if link_type.code in product_links:
            link_obj.browse(product_links[link_type.code]).write({
                "type_id": link_type.id})


def _enable_constraint(cr, env):
    """
    As we need to re-enable constraint, mark module as to upgrade.

    """
    cr.execute(
        'ALTER TABLE "%s" ALTER COLUMN "%s" SET NOT NULL' %
        ('product_template_link', 'type_id'))


def migrate(cr, version):

    with odoo.api.Environment.manage():
        env = odoo.api.Environment(cr, odoo.SUPERUSER_ID, {})

    _remove_duplicates(cr, env)
    _set_link_types(cr, env)
    _enable_constraint(cr, env)
