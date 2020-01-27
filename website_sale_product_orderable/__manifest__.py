# © 2020 - Today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    'name': 'Website Sale Product Orderable',
    'version': '1.0.0',
    'author': 'Numigi, Odoo Community Association (OCA)',
    'maintainer': 'Numigi',
    'license': 'LGPL-3',
    'category': 'Human Resources',
    'summary': 'Add two fields in the form views of product: Orderable and Display Message',
    'category': 'Website',
    'application': False,
    'installable': True,
    'depends': [
        'website_sale',
    ],
    'data': [
        'product_template_views.xml'
    ]
}
