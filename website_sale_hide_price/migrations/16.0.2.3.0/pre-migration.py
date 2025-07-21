# Copyright 2025 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.set_xml_ids_noupdate_value(
        env,
        "website_sale_hide_price",
        [
            "price_dynamic_filter_template_product_product",
            "filter_template_dynamic_product_product_borderless_2",
            "filter_template_dynamic_product_product_add_to_cart",
            "filter_template_dynamic_product_product_horizontal_card",
            "filter_template_dynamic_product_product_banner",
        ],
        False,
    )
