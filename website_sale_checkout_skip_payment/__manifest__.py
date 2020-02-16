# Copyright 2017 Sergio Teruel <sergio.teruel@tecnativa.com>
# Copyright 2017 David Vidal <david.vidal@tecnativa.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    'name': 'Website Sale Checkout Skip Payment',
    'summary': 'Skip payment for logged users in checkout process',
    'version': '12.0.1.1.0',
    'category': 'Website',
    'website': 'https://www.tecnativa.com',
    'author': 'Tecnativa, Odoo Community Association (OCA)',
    'license': 'LGPL-3',
    'application': False,
    'installable': True,
    'depends': [
        'website_sale',
    ],
    'data': [
        'views/assets.xml',
        'views/website_sale_skip_payment.xml',
        'views/website_sale_template.xml',
        'views/partner_view.xml',
    ],
}
