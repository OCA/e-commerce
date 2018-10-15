# Copyright 2018 Denis Mudarisov (IT-Projects LLC)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Website form first name and last name",
    "summary": """
            Allow to change name field in form to first name and last name
    """,
    "version": "11.0.1.0.0",
    "author": "IT-Projects LLC, "
              "Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "maintainer": "IT-Projects LLC",
    "category": "Extra Tools",
    "website": "https://github.com/OCA/e-commerce",
    "depends": [
        "website_sale",
        "partner_firstname",
    ],
    "data": [
        "data/data.xml",
    ],
    "installable": True,
}
