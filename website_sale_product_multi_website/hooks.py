def post_init_hook(env):
    for rec in env["product.template"].with_context(active_test=False).search([]):
        rec.website_ids += rec.website_id
