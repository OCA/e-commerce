# Copyright 2020 Tecnativa - David Vidal
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Display product reference in e-commerce",
    "version": "19.0.1.0.0",
    "category": "Website",
    "website": "https://github.com/OCA/e-commerce",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": ["website_sale"],
    "data": ["data/snippet_filter_data.xml", "views/website_sale_views.xml"],
    "assets": {
        "website.website_builder_assets": [
            "website_sale_product_reference_displayed/static/src/website_builder/**/*",
        ],
    },
}
