import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo12-addons-oca-e-commerce",
    description="Meta package for oca-e-commerce Odoo addons",
    version=version,
    install_requires=[
        'odoo12-addon-website_sale_attribute_filter_category',
        'odoo12-addon-website_sale_checkout_country_vat',
        'odoo12-addon-website_sale_checkout_skip_payment',
        'odoo12-addon-website_sale_product_attribute_filter_visibility',
        'odoo12-addon-website_sale_product_attribute_value_filter_existing',
        'odoo12-addon-website_sale_product_detail_attribute_image',
        'odoo12-addon-website_sale_require_legal',
        'odoo12-addon-website_sale_require_login',
        'odoo12-addon-website_sale_secondary_unit',
        'odoo12-addon-website_sale_show_company_data',
        'odoo12-addon-website_sale_stock_available_display',
        'odoo12-addon-website_sale_suggest_create_account',
        'odoo12-addon-website_sale_vat_required',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
    ]
)
