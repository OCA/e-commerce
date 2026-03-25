# Copyright 2025 Alberto Martínez <alberto.martinez@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Website Sale Cart Add Product Xlsx Csv",
    "summary": "Adds button to import xlsx or csv in website cart",
    "version": "17.0.1.0.1",
    "website": "https://github.com/OCA/e-commerce",
    "author": "Sygel, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "website_sale_stock",
    ],
    "external_dependencies": {"python": ["openpyxl"]},
    "data": [
        "data/import_file_example.xml",
        "views/cart_templates.xml",
        "views/res_config_settings.xml",
    ],
}
