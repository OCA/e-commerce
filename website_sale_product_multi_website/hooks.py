from odoo import SUPERUSER_ID, api


def post_init_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    for rec in env["product.template"].with_context(active_test=False).search([]):
        rec.website_ids += rec.website_id
