import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo10-addons-oca-e-commerce",
    description="Meta package for oca-e-commerce Odoo addons",
    version=version,
    install_requires=[
        'odoo10-addon-product_multi_link',
        'odoo10-addon-product_template_multi_link',
        'odoo10-addon-website_sale_affiliate',
        'odoo10-addon-website_sale_cart_selectable',
        'odoo10-addon-website_sale_category_alphabetic',
        'odoo10-addon-website_sale_checkout_country_vat',
        'odoo10-addon-website_sale_default_country',
        'odoo10-addon-website_sale_hide_price',
        'odoo10-addon-website_sale_price_tier',
        'odoo10-addon-website_sale_require_legal',
        'odoo10-addon-website_sale_require_login',
        'odoo10-addon-website_sale_search_fuzzy',
        'odoo10-addon-website_sale_select_qty',
        'odoo10-addon-website_sale_suggest_create_account',
        'odoo10-addon-website_sale_wishlist',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
    ]
)
