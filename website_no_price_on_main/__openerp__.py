# -*- coding: utf-8 -*-
# © 2017 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "No prices visualized on main website",
    "version": "9.0.1.0.0",
    "author": "Odoo Community Association (OCA), Therp BV",
    "license": "AGPL-3",
    "category": "Website",
    "summary": "Do not show th epricing on the main website",
    "depends": [
        "website_product_name",
        "base_view_inheritance_extension",
    ],
    "data": [
        'views/templates.xml',
        'views/website_config_settings.xml',
        'views/sale_order.xml',
        'data/ir_ui_view.xml',
    ],
    "installable": True,
}
