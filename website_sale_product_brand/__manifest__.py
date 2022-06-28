# © 2016 Serpent Consulting Services Pvt. Ltd. (http://www.serpentcs.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Product Brand Filtering in Website",
    "category": "e-commerce",
    "author": "Serpent Consulting Services Pvt. Ltd., "
    "Tecnativa, "
    "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/e-commerce",
    "version": "14.0.1.1.0",
    "license": "AGPL-3",
    "depends": ["product_brand", "website_sale"],
    "data": [
        "security/ir.model.access.csv",
        "data/website_menu.xml",
        "views/product_brand.xml",
        "views/assets.xml",
        "views/product_brand_views.xml",
    ],
    "demo": [
        "demo/product_brand_demo.xml",
        "demo/product_product_demo.xml",
    ],
    "installable": True,
}
