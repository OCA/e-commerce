# Copyright 2018 Simone Rubino - Agile Business Group
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo.tests import HttpCase


class TestFrontend(HttpCase):

    def setUp(self):
        super(TestFrontend, self).setUp()
        self.sale_type_model = self.env['sale.order.type']

        self.partner = self.env.ref('base.partner_admin')
        self.sale_type = self.create_sale_type()

    def create_sale_type(self):
        self.sequence = self.env['ir.sequence'].create({
            'name': 'Test Sales Order',
            'code': 'sale.order',
            'prefix': 'TSO',
            'padding': 3,
        })
        self.journal = self.env['account.journal'].search(
            [('type', '=', 'sale')], limit=1)
        self.warehouse = self.env.ref('stock.stock_warehouse_shop0')
        self.immediate_payment = self.env.ref(
            'account.account_payment_term_immediate')
        self.sale_pricelist = self.env.ref('product.list0')
        self.free_carrier = self.env.ref('account.incoterm_FCA')
        return self.sale_type_model.create({
            'name': 'Test Sale Order Type',
            'sequence_id': self.sequence.id,
            'journal_id': self.journal.id,
            'warehouse_id': self.warehouse.id,
            'picking_policy': 'one',
            'payment_term_id': self.immediate_payment.id,
            'pricelist_id': self.sale_pricelist.id,
            'incoterm_id': self.free_carrier.id,
        })

    def test_website_sale_order_type(self):
        self.partner.sale_type = self.sale_type
        existing_orders = self.env['sale.order'].search([])
        # In frontend, create an order
        tour_prefix = "odoo.__DEBUG__.services['web_tour.tour']"
        self.phantom_js(
            "/shop",
            tour_prefix + ".run('website_sale_order_type_tour')",
            tour_prefix + ".tours.website_sale_order_type_tour.ready",
            login="admin")
        created_order = self.env['sale.order'].search([
            ('id', 'not in', existing_orders.ids)])
        self.assertEqual(created_order.type_id, self.sale_type)
