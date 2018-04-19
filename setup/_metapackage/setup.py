import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo8-addons-oca-e-commerce",
    description="Meta package for oca-e-commerce Odoo addons",
    version=version,
    install_requires=[
        'odoo8-addon-product_links',
        'odoo8-addon-website_product_share',
        'odoo8-addon-website_product_show_uom',
        'odoo8-addon-website_sale_cart_preview',
        'odoo8-addon-website_sale_cart_selectable',
        'odoo8-addon-website_sale_category_megamenu',
        'odoo8-addon-website_sale_checkout_comment',
        'odoo8-addon-website_sale_checkout_country_vat',
        'odoo8-addon-website_sale_default_country',
        'odoo8-addon-website_sale_product_brand',
        'odoo8-addon-website_sale_product_legal',
        'odoo8-addon-website_sale_recently_viewed_products',
        'odoo8-addon-website_sale_require_legal',
        'odoo8-addon-website_sale_require_login',
        'odoo8-addon-website_sale_suggest_create_account',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
    ]
)
