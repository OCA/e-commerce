# © 2016 Serpent Consulting Services Pvt. Ltd. (http://www.serpentcs.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Product Brand Filtering in Website',
    'category': 'e-commerce',
    'author': "Serpent Consulting Services Pvt. Ltd., "
              "Tecnativa, "
              "Odoo Community Association (OCA)",
    'website': 'https://github.com/OCA/e-commerce',
    'version': '12.0.1.3.0',
    'license': 'AGPL-3',
    'depends': [
        'product_brand',
        'website_sale'
    ],
    'data': [
        "data/website_menu.xml",
        "views/product_brand.xml",
        "views/product_brand_views.xml",
    ],
    'demo': [
        "demo/assets.xml",
        "demo/product_brand_demo.xml",
        "demo/product_product_demo.xml",
    ],
    'installable': True,
}
