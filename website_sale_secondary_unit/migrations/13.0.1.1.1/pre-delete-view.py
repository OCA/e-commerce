from odoo import SUPERUSER_ID, api


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    views_to_unlink = env.ref(
        "website_sale_secondary_unit.product_template_website_publish_form_view", False
    )
    if views_to_unlink:
        views_to_unlink.unlink()
