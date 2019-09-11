# Copyright 2015 Agile Business Group sagl (<http://www.agilebg.com>)
# Copyright 2017 Jairo Llopis <jairo.llopis@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'e-commerce required VAT',
    'summary': 'VAT number required in checkout form',
    'version': '12.0.1.0.0',
    'category': 'Website',
    'author': "Agile Business Group, "
              "Tecnativa, "
              "Odoo Community Association (OCA)",
    'website': 'https://github.com/OCA/e-commerce',
    'license': 'AGPL-3',
    'depends': [
        'website_sale',
        'base_vat',
    ],
    'data': [
        'views/templates.xml',
    ],
    'demo': [
        'demo/demo_assets.xml',
    ],
    'installable': True,
    'auto_install': False,
}
