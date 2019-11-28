# Copyright 2019 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


def post_init_hook(cr, registry):
    """
    At installation time, set allow_uom_sell field as true for all products
    that have already been created.
    """
    cr.execute("""
        UPDATE product_template
        SET allow_uom_sell=true
        WHERE allow_uom_sell IS NULL;
    """)
