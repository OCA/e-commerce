# -*- coding: utf-8 -*-
# Copyright 2017 Jairo Llopis <jairo.llopis@tecnativa.com>
# Copyright 2017 David Vidal <david.vidal@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import mock
from contextlib import contextmanager
from openerp.tests.common import SavepointCase


class B2BCase(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(B2BCase, cls).setUpClass()
        cls.website = cls.env["website"].search([], limit=1)
        with cls._mock():
            cls.pricelist = cls.website.get_current_pricelist()
        cls.partner = cls.env["res.partner"].create({
            "name": "good boy",
        })
        cls.tax = cls.env["account.tax"].create({
            "name": "test",
            "amount": 10,
        })
        cls.attribute = cls.env["product.attribute"].create({
            "name": "color",
        })
        cls.value = cls.env["product.attribute.value"].create({
            "price_extra": 10,
            "name": "red",
            "attribute_id": cls.attribute.id,
        })
        cls.product_template = (
            cls.env["product.template"].with_context(
                pricelist=cls.pricelist.id,
                uom=False,
            )
            .create({
                "name": "product template 1",
                "list_price": 10,
                "taxes_id": [(6, 0, cls.tax.ids)],
                "attribute_line_ids": [(0, 0, {
                    "attribute_id": cls.attribute.id,
                    "value_ids": [(6, 0, cls.value.ids)],
                })],
            }))
        cls.env["product.attribute.price"].create({
            "product_tmpl_id": cls.product_template.id,
            "value_id": cls.value.id,
            "price_extra": 10,
        })
        cls.product = cls.product_template.product_variant_ids
        cls.product.list_price = 10
        cls.sale_order = cls.env["sale.order"].create({
            "partner_id": cls.partner.id,
            "order_line": [(0, 0, {
                "product_id": cls.product.id,
            })],
        })

    @classmethod
    @contextmanager
    def _mock(cls):
        """Make the process think we are under :attr:`website` context."""
        with mock.patch("openerp.addons.website.models"
                        ".website.website.get_current_website",
                        return_value=cls.website), \
                mock.patch("openerp.addons.website_sale.models"
                           ".sale_order.request",
                           website=cls.website):
            yield

    def test_product_b2b(self):
        """Product prices in B2B mode."""
        self.assertEqual(
            self.product.lst_price,
            20,
        )
        self.assertEqual(
            self.product.price_extra,
            10,
        )

    def test_product_b2c(self):
        """Product prices in B2C mode."""
        with self._mock():
            self.assertEqual(
                self.product.with_context(
                    b2c_prices=True, website_id=self.website.id).lst_price,
                22,
            )
            self.assertEqual(
                self.product.with_context(
                    b2c_prices=True, website_id=self.website.id).price_extra,
                11,
            )

    def test_product_template_b2b(self):
        """Product template prices in B2B mode."""
        self.assertEqual(
            self.product_template.price,
            10,
        )

    def test_product_template_b2c(self):
        """Product template prices in B2C mode."""
        with self._mock():
            self.assertEqual(
                self.product_template.with_context(
                    b2c_prices=True, website_id=self.website.id).price,
                11,
            )

    def test_sale_order_b2b(self):
        """Sale order line prices in B2B mode."""
        self.assertEqual(
            self.sale_order.order_line.discounted_price,
            20,
        )

    def test_sale_order_b2c(self):
        """Sale order line prices in B2C mode."""
        with self._mock():
            self.assertEqual(
                self.sale_order.with_context(
                    b2c_prices=True,
                    website_id=self.website.id).order_line.discounted_price,
                22,
            )
