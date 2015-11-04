from openerp.osv import orm, fields


class Invoice(orm.Model):
    _inherit = 'account.invoice'

    _columns = {
        'sale_order_ids': fields.many2many(
            'sale.order',
            'sale_order_invoice_rel', 'invoice_id', 'order_id',
            'Sales Orders', readonly=True, help="""This is the list of sales
             orders that have generated this invoice."""),
    }
