import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo13-addons-oca-e-commerce",
    description="Meta package for oca-e-commerce Odoo addons",
    version=version,
    install_requires=[
        'odoo13-addon-product_template_multi_link',
        'odoo13-addon-product_template_multi_link_date_span',
        'odoo13-addon-product_variant_multi_link',
        'odoo13-addon-website_sale_attribute_filter_category',
        'odoo13-addon-website_sale_attribute_filter_order',
        'odoo13-addon-website_sale_attribute_filter_price',
        'odoo13-addon-website_sale_checkout_skip_payment',
        'odoo13-addon-website_sale_hide_empty_category',
        'odoo13-addon-website_sale_hide_price',
        'odoo13-addon-website_sale_product_attribute_filter_visibility',
        'odoo13-addon-website_sale_product_attribute_value_filter_existing',
        'odoo13-addon-website_sale_product_brand',
        'odoo13-addon-website_sale_product_detail_attribute_image',
        'odoo13-addon-website_sale_product_minimal_price',
        'odoo13-addon-website_sale_require_login',
        'odoo13-addon-website_sale_stock_list_preview',
        'odoo13-addon-website_sale_suggest_create_account',
        'odoo13-addon-website_sale_vat_required',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
    ]
)
