import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo11-addons-oca-e-commerce",
    description="Meta package for oca-e-commerce Odoo addons",
    version=version,
    install_requires=[
        'odoo11-addon-website_sale_default_country',
        'odoo11-addon-website_sale_require_legal',
        'odoo11-addon-website_sale_require_login',
        'odoo11-addon-website_sale_suggest_create_account',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
    ]
)
