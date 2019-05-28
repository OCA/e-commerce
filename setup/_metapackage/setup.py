import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo11-addons-oca-e-commerce",
    description="Meta package for oca-e-commerce Odoo addons",
    version=version,
    install_requires=[
        'odoo11-addon-website_sale_attribute_filter_category',
        'odoo11-addon-website_sale_checkout_skip_payment',
        'odoo11-addon-website_sale_default_country',
        'odoo11-addon-website_sale_firstname',
        'odoo11-addon-website_sale_hide_empty_category',
        'odoo11-addon-website_sale_hide_price',
        'odoo11-addon-website_sale_product_attribute_filter_visibility',
        'odoo11-addon-website_sale_product_brand',
        'odoo11-addon-website_sale_product_detail_attribute_image',
        'odoo11-addon-website_sale_require_legal',
        'odoo11-addon-website_sale_require_login',
        'odoo11-addon-website_sale_secondary_unit',
        'odoo11-addon-website_sale_suggest_create_account',
        'odoo11-addon-website_sale_vat_required',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
    ]
)
