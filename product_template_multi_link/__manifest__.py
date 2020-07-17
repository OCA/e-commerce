# Copyright 2017-Today GRAP (http://www.grap.coop).
# @author Sylvain LE GAL <https://twitter.com/legalsylvain>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Product Multi Links (Template)",
    "version": "13.0.1.1.1",
    "category": "Generic Modules",
    "author": "GRAP, ACSONE SA/NV, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/e-commerce",
    "license": "AGPL-3",
    "depends": ["sale"],
    "data": [
        "data/product_template_link_type.xml",
        "security/product_template_link_type.xml",
        "views/product_template_link_type.xml",
        "security/ir.model.access.csv",
        "views/action.xml",
        "views/product_template_view.xml",
        "views/product_template_link_view.xml",
        "views/menu.xml",
    ],
    "demo": ["demo/product_template_link_type.xml", "demo/product_template_link.xml"],
    "installable": True,
}
