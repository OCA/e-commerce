# Copyright 2020 Tecnativa - David Vidal
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    'name': 'Website Sale Product Sort',
    'summary': 'Allow to define default sort criteria for e-commerce',
    'version': '12.0.1.0.0',
    'development_status': 'Beta',
    'category': 'Website',
    'website': 'https://github.com/OCA/e-commerce',
    'author': 'Tecnativa, Odoo Community Association (OCA)',
    'license': 'AGPL-3',
    'depends': [
        'website_sale',
    ],
    'data': [
        "views/website_sale_sort.xml",
        "views/res_config_settings_view.xml",
    ],
    'application': False,
    'installable': True,
}
