{
    'name': 'Website Portal for Sales',
    'category': 'Website',
    'summary': (
        'Add your sales document in the frontend portal (sales order'
        ', quotations, invoices)'
    ),
    'version': '8.0.1.0.0',
    'author': 'Odoo SA, MONK Software, Vauxoo',
    'website':
        'https://www.odoo.com/, http://www.wearemonk.com, http://vauxoo.com',
    'depends': [
        'sale',
        'website_portal',
    ],
    'data': [
        'templates/website_portal_sale.xml',
        'templates/website_portal.xml',
        'templates/website.xml',
    ],
    'demo': [
        'demo/sale_order.xml',
    ],
    'installable': True,
}
