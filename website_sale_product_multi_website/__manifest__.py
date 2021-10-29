{
    "name": "Multi-website product",
    "summary": "Show products in many web-sites",
    "version": "13.0.1.0.0",
    "category": "Website",
    "author": "Odoo Community Association (OCA), Adhoc S.A.",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": ["website_sale"],
    "data": ["views/product_template_views.xml"],
    "demo": [],
    "post_init_hook": "post_init_hook",
    "uninstall_hook": "uninstall_hook",
}
