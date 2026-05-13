{
    "name": "Website Sale Product Multi Website",
    "summary": "Show products in many websites",
    "version": "17.0.1.0.1",
    "category": "Website",
    "author": "Odoo Community Association (OCA), Adhoc S.A.",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": ["website_sale"],
    "data": ["views/product_template_views.xml"],
    "post_init_hook": "post_init_hook",
    "website": "https://github.com/OCA/e-commerce",
}
