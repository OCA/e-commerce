# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
{
    "name": "Website Sale Cart No Redirect",
    "summary": "Avoid redirection to the cart page when adding a product to cart",
    "version": "13.0.1.0.0",
    "category": "Website",
    "website": "https://github.com/OCA/e-commerce",
    "author": "Tecnativa, Odoo Community Association (OCA), Odoo SA",
    "license": "LGPL-3",
    "depends": ["website_sale"],
    "data": [
        "views/assets.xml",
        "views/res_config_settings_views.xml",
        "templates/templates.xml",
    ],
    "installable": True,
}
