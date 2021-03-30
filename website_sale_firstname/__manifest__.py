# Copyright 2020 Algoritmun Ltd.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Website form first name and last name",
    "summary": """
            Allow to change name field in form to first name and last name
    """,
    "version": "13.0.1.0.0",
    "author": "ALGORITMUN CIA. LTDA., "
              "Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "maintainer": "ALGORITMUN CIA. LTDA.",
    "category": "Extra Tools",
    "website": "https://github.com/OCA/e-commerce",
    "depends": [
        "website_sale",
    ],
    "data": [
        "data/data.xml",
        "views/portal_templates.xml",
        "views/templates.xml",
    ],
    "installable": True,
}
