# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from freezegun import freeze_time

from odoo.tests.common import SavepointCase


@freeze_time("2020-07-29")
class TestProductTemplateLinkDateSpan(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.link_type = cls.env.ref(
            "product_template_multi_link.product_template_link_type_cross_selling"
        )
        cls.link = cls.env["product.template.link"].create(
            {
                "left_product_tmpl_id": cls.env.ref("product.product_product_1").id,
                "right_product_tmpl_id": cls.env.ref("product.product_product_2").id,
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
