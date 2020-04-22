# Copyright 2020 Tecnativa - Ernesto Tejeda
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import SavepointCase


class SaleStockAvailableInfoPopup(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(SaleStockAvailableInfoPopup, cls).setUpClass()
        user_group_stock_user = cls.env.ref('stock.group_stock_user')
        cls.user_stock_user = cls.env['res.users'].create({
            'name': 'Pauline Poivraisselle',
            'login': 'pauline',
            'email': 'p.p@example.com',
            'notification_type': 'inbox',
            'groups_id': [(6, 0, [user_group_stock_user.id])]})
        cls.product = cls.env['product.product'].create({
            'name': 'Storable product',
            'type': 'product',
        })
        cls.stock_location = cls.env.ref('stock.stock_location_stock')
        cls.customers_location = cls.env.ref('stock.stock_location_customers')
        cls.suppliers_location = cls.env.ref('stock.stock_location_suppliers')
        cls.env['stock.quant'].create({
            'product_id': cls.product.id,
            'location_id': cls.stock_location.id,
            'quantity': 40.0})
        cls.picking_out = cls.env['stock.picking'].create({
            'picking_type_id': cls.env.ref('stock.picking_type_out').id,
            'location_id': cls.stock_location.id,
            'location_dest_id': cls.customers_location.id})
        cls.env['stock.move'].create({
            'name': 'a move',
            'product_id': cls.product.id,
            'product_uom_qty': 3.0,
            'product_uom': cls.product.uom_id.id,
            'picking_id': cls.picking_out.id,
            'location_id': cls.stock_location.id,
            'location_dest_id': cls.customers_location.id})
        cls.picking_in = cls.env['stock.picking'].create({
            'picking_type_id': cls.env.ref('stock.picking_type_in').id,
            'location_id': cls.suppliers_location.id,
            'location_dest_id': cls.stock_location.id})
        cls.env['stock.move'].create({
            'restrict_partner_id': cls.user_stock_user.partner_id.id,
            'name': 'another move',
            'product_id': cls.product.id,
            'product_uom_qty': 5.0,
            'product_uom': cls.product.uom_id.id,
            'picking_id': cls.picking_in.id,
            'location_id': cls.suppliers_location.id,
            'location_dest_id': cls.stock_location.id})

    def test_get_combination_info(self):
        product_tmpl = self.product.product_tmpl_id
        combination_info = product_tmpl.with_context(
            website_sale_stock_get_quantity=True,
        )._get_combination_info()
        self.assertEqual(
            combination_info['virtual_available'],
            40,
        )
        self.picking_out.action_confirm()
        self.picking_in.action_assign()
        combination_info = product_tmpl.with_context(
            website_sale_stock_get_quantity=True,
        )._get_combination_info()
        self.assertEqual(
            combination_info['virtual_available'],
            self.product.immediately_usable_qty
        )
