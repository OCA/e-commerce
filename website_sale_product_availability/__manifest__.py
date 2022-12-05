# Copyright 2022 Coop IT Easy SC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Website Sale Product Availability",
    "summary": """
        Display the quantity of products available on the product overview.""",
    "version": "12.0.1.0.0",
    "category": "Website",
    "website": "https://github.com/OCA/e-commerce",
    "author": "Coop IT Easy SC",
    "maintainers": ["carmenbianca"],
    "license": "AGPL-3",
    "application": False,
    "depends": [
        "website_sale",
        "website_sale_stock",
    ],
    "excludes": [],
    "data": [
        "views/templates.xml",
    ],
    "demo": [],
    "qweb": [],
}
