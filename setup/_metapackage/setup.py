import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo-addons-oca-e-commerce",
    description="Meta package for oca-e-commerce Odoo addons",
    version=version,
    install_requires=[
        'odoo-addon-website_sale_attribute_filter_form_submit>=16.0dev,<16.1dev',
        'odoo-addon-website_sale_attribute_filter_multiselect>=16.0dev,<16.1dev',
        'odoo-addon-website_sale_cart_expire>=16.0dev,<16.1dev',
        'odoo-addon-website_sale_comparison_hide_price>=16.0dev,<16.1dev',
        'odoo-addon-website_sale_hide_price>=16.0dev,<16.1dev',
        'odoo-addon-website_sale_order_type>=16.0dev,<16.1dev',
        'odoo-addon-website_sale_product_attribute_filter_collapse>=16.0dev,<16.1dev',
        'odoo-addon-website_sale_product_attribute_value_filter_existing>=16.0dev,<16.1dev',
        'odoo-addon-website_sale_product_brand>=16.0dev,<16.1dev',
        'odoo-addon-website_sale_product_description>=16.0dev,<16.1dev',
        'odoo-addon-website_sale_product_detail_attribute_image>=16.0dev,<16.1dev',
        'odoo-addon-website_sale_product_reference_displayed>=16.0dev,<16.1dev',
        'odoo-addon-website_sale_stock_available>=16.0dev,<16.1dev',
        'odoo-addon-website_snippet_product_category>=16.0dev,<16.1dev',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 16.0',
    ]
)
