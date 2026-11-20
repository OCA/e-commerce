# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Website Sale Stock Sold Out Form",
    "summary": """This module allows to display the 'Sold Out' status on
    product form""",
    "version": "18.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/e-commerce",
    "depends": ["product", "website_sale_stock"],
    "data": [
        "views/product_product.xml",
    ],
}
