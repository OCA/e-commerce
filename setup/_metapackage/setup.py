import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo12-addons-oca-e-commerce",
    description="Meta package for oca-e-commerce Odoo addons",
    version=version,
    install_requires=[
        'odoo12-addon-website_sale_attribute_filter_category',
        'odoo12-addon-website_sale_attribute_filter_order',
        'odoo12-addon-website_sale_attribute_filter_price',
        'odoo12-addon-website_sale_b2x_alt_price',
        'odoo12-addon-website_sale_cart_selectable',
        'odoo12-addon-website_sale_category_description',
        'odoo12-addon-website_sale_checkout_country_vat',
        'odoo12-addon-website_sale_checkout_skip_payment',
        'odoo12-addon-website_sale_exception',
        'odoo12-addon-website_sale_hide_empty_category',
        'odoo12-addon-website_sale_hide_price',
        'odoo12-addon-website_sale_product_attachment',
        'odoo12-addon-website_sale_product_attribute_filter_visibility',
        'odoo12-addon-website_sale_product_attribute_value_filter_existing',
        'odoo12-addon-website_sale_product_brand',
        'odoo12-addon-website_sale_product_detail_attribute_image',
        'odoo12-addon-website_sale_product_detail_attribute_value_image',
        'odoo12-addon-website_sale_product_minimal_price',
        'odoo12-addon-website_sale_product_model_viewer',
        'odoo12-addon-website_sale_product_reference_displayed',
        'odoo12-addon-website_sale_product_sort',
        'odoo12-addon-website_sale_product_style_badge',
        'odoo12-addon-website_sale_require_legal',
        'odoo12-addon-website_sale_require_login',
        'odoo12-addon-website_sale_secondary_unit',
        'odoo12-addon-website_sale_show_company_data',
        'odoo12-addon-website_sale_stock_available',
        'odoo12-addon-website_sale_stock_available_display',
        'odoo12-addon-website_sale_stock_force_block',
        'odoo12-addon-website_sale_stock_provisioning_date',
        'odoo12-addon-website_sale_suggest_create_account',
        'odoo12-addon-website_sale_tax_toggle',
        'odoo12-addon-website_sale_vat_required',
        'odoo12-addon-website_sale_wishlist_keep',
        'odoo12-addon-website_snippet_carousel_product',
        'odoo12-addon-website_snippet_product_category',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
    ]
)
