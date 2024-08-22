# Copyright 2024 Unai Beristain - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).


# Add to Cart button on product page
# Necessary to know product_id to add to cart
def pre_init_hook(cr):
    cr.execute(
        """
            UPDATE ir_ui_view
            SET active = TRUE
            WHERE key = 'website_sale.products_add_to_cart'
        """
    )
