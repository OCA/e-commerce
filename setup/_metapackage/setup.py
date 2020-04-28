import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo13-addons-oca-e-commerce",
    description="Meta package for oca-e-commerce Odoo addons",
    version=version,
    install_requires=[
        'odoo13-addon-website_sale_checkout_skip_payment',
        'odoo13-addon-website_sale_product_attribute_filter_visibility',
        'odoo13-addon-website_sale_product_brand',
        'odoo13-addon-website_sale_require_login',
        'odoo13-addon-website_sale_stock_list_preview',
        'odoo13-addon-website_sale_suggest_create_account',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
    ]
)
