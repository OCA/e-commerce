{
    "name": "Multi-website product",
    "summary": "Show products in many web-sites",
    "version": "18.0.1.1.0",
    "category": "Website",
    "author": "Odoo Community Association (OCA), Adhoc S.A.",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": ["website_sale"],
    "data": [
        "views/product_template_views.xml",
        "security/website_sale_product_multi_website_security.xml",
        "security/ir.model.access.csv",
    ],
    "demo": [],
    "post_init_hook": "post_init_hook",
    "website": "https://github.com/OCA/e-commerce",
}
