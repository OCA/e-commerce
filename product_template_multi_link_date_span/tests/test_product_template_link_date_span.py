# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from freezegun import freeze_time

from odoo import exceptions
from odoo.tests.common import SavepointCase


@freeze_time("2020-07-29")
class TestProductTemplateLinkDateSpan(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.link_type = cls.env["product.template.link.type"].get_by_code(
            "cross-selling"
        )
        cls.link_type.limited_by_dates = True
        cls.prod1 = prod1 = cls.env.ref("product.product_product_1")
        cls.prod2 = prod2 = cls.env.ref("product.product_product_2")
        cls.link = cls.env["product.template.link"].create(
            {
                "left_product_tmpl_id": prod1.id,
                "right_product_tmpl_id": prod2.id,
                "type_id": cls.link_type.id,
            }
        )

    def test_active_link(self):
        self.assertTrue(self.link.is_link_active)
        self.link.date_start = "2020-07-29"
        self.assertTrue(self.link.is_link_active)
        self.link.date_start = "2020-01-29"
        self.link.date_end = "2020-12-31"
        self.assertTrue(self.link.is_link_active)
        self.link.date_start = ""
        self.assertTrue(self.link.is_link_active)

    def test_inactive_link(self):
        self.link.date_start = "2021-01-01"
        self.assertFalse(self.link.is_link_active)
        self.link.date_start = "2020-01-01"
        self.link.date_end = "2020-07-01"
        self.assertFalse(self.link.is_link_active)
        self.link.date_start = ""
        self.link.date_end = "2020-07-28"
        self.assertFalse(self.link.is_link_active)
        # Exception: if limitation is off the link is active anyway
        self.link_type.limited_by_dates = False
        self.assertTrue(self.link.is_link_active)

    def test_mandatory_date(self):
        link_type = self.env["product.template.link.type"].get_by_code("up-selling")
        link_type.limited_by_dates = True
        link_type.mandatory_date_start = True
        message = "A start date is required according to link type"
        with self.assertRaisesRegex(exceptions.UserError, message):
            self.env["product.template.link"].create(
                {
                    "left_product_tmpl_id": self.prod1.id,
                    "right_product_tmpl_id": self.prod2.id,
                    "type_id": link_type.id,
                }
            )
