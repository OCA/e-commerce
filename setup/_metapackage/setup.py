import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo9-addons-oca-e-commerce",
    description="Meta package for oca-e-commerce Odoo addons",
    version=version,
    install_requires=[
        'odoo9-addon-product_multi_link',
        'odoo9-addon-website_sale_b2c',
        'odoo9-addon-website_sale_checkout_country_vat',
        'odoo9-addon-website_sale_checkout_skip_payment',
        'odoo9-addon-website_sale_default_country',
        'odoo9-addon-website_sale_product_brand',
        'odoo9-addon-website_sale_qty',
        'odoo9-addon-website_sale_require_legal',
        'odoo9-addon-website_sale_require_login',
        'odoo9-addon-website_sale_stock_control',
        'odoo9-addon-website_sale_suggest_create_account',
        'odoo9-addon-website_sale_vat_required',
        'odoo9-addon-website_sale_wishlist',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
    ]
)
