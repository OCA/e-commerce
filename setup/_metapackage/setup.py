import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo-addons-oca-e-commerce",
    description="Meta package for oca-e-commerce Odoo addons",
    version=version,
    install_requires=[
        'odoo-addon-website_sale_cart_expire>=15.0dev,<15.1dev',
        'odoo-addon-website_sale_checkout_country_vat>=15.0dev,<15.1dev',
        'odoo-addon-website_sale_checkout_skip_payment>=15.0dev,<15.1dev',
        'odoo-addon-website_sale_comparison_hide_price>=15.0dev,<15.1dev',
        'odoo-addon-website_sale_hide_empty_category>=15.0dev,<15.1dev',
        'odoo-addon-website_sale_hide_price>=15.0dev,<15.1dev',
        'odoo-addon-website_sale_product_brand>=15.0dev,<15.1dev',
        'odoo-addon-website_sale_product_description>=15.0dev,<15.1dev',
        'odoo-addon-website_sale_product_detail_attribute_value_image>=15.0dev,<15.1dev',
        'odoo-addon-website_sale_product_reference_displayed>=15.0dev,<15.1dev',
        'odoo-addon-website_sale_require_login>=15.0dev,<15.1dev',
        'odoo-addon-website_sale_secondary_unit>=15.0dev,<15.1dev',
        'odoo-addon-website_sale_suggest_create_account>=15.0dev,<15.1dev',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 15.0',
    ]
)
