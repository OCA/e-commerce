# Copyright 2020 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


def uninstall_hook(cr, registry):
    """Restore inventory_availability to default value for products"""
    cr.execute("""
        UPDATE product_template
        SET inventory_availability = 'never'
        WHERE inventory_availability = 'custom_block'
    """)
