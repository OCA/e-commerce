# Copyright 2023 Tecnativa - Pilar Vargas
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.logged_query(
        env.cr,
        """
DELETE FROM ir_ui_view
WHERE key =
    'website_sale_product_attribute_filter_category.products_attributes_collapsible'
AND website_id IS NOT NULL
        """,
    )
