from odoo import SUPERUSER_ID, api


def post_init_hook(cr, _registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    for rec in (
        env["product.template"]
        .with_context(active_test=False)
        .search([("website_id", "!=", False)])
    ):
        rec.website_ids += rec.website_id


def uninstall_hook(cr, _registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    for rec in (
        env["product.template"]
        .with_context(active_test=False)
        .search([("website_ids", "!=", False)])
    ):
        if len(rec.website_ids) == 1:
            rec.website_id = rec.website_ids[0]
        else:
            rec.website_id = False
