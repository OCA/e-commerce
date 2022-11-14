# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)
from odoo.tests import TransactionCase


class TestWebsiteSaleCustomFilter(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Websites
        cls.website_1 = cls.env.ref("website.default_website")
        cls.website_2 = cls.env.ref("website.website2")

        cls.web_custom_filter = cls.env["website.sale.custom.filter"]
        cls.web_custom_filter_value = cls.env["website.sale.custom.filter.value"]

        # numerical filter data
        cls.price_field = cls.env["ir.model.fields"].search(
            [("name", "=", "list_price")], limit=1
        )
        cls.numerical_filter_vals = {
            "name": "price filter",
            "website_category_ids": False,
            "filter_type": "numerical",
            "numerical_filter_field_id": cls.price_field.id,
            "website_ids": [(4, cls.website_1.id)],
        }

        # value filter data
        cls.ir_filters_service_type = cls.env["ir.filters"].create(
            {
                "name": "product cheaper than 100",
                "model_id": "product.template",
                "domain": "[['service_type', '=', 'manual']]",
            }
        )

    def test_website_filters(self):
        # create numerical/range filter
        self.custom_numerical_filter_price = self.web_custom_filter.create(
            self.numerical_filter_vals
        )

        # make sure filter active only for website_1
        self.assertIn(
            self.custom_numerical_filter_price.id,
            self.website_1.get_website_sale_custom_filters().ids,
        )

        # create value/checkbox filter and its values
        value_filter_data = {
            "name": "service_type filter",
            "website_category_ids": False,
            "filter_type": "value",
            "website_ids": [(4, self.website_2.id)],
        }
        self.custom_value_filter_service = self.web_custom_filter.create(
            value_filter_data
        )

        # create values for this type of filter
        custom_filter_value = {
            "name": "warranty set",
            "value_filter_id": self.ir_filters_service_type.id,
            "custom_filter_id": self.custom_value_filter_service.id,
        }
        self.checkbox_filter_value_set = self.web_custom_filter_value.create(
            custom_filter_value
        )

        # make sure recordset on filter is correct
        products_with_warranty = self.env["product.template"].search(
            [("service_type", "=", "manual")]
        )
        self.assertEqual(
            products_with_warranty.ids,
            self.checkbox_filter_value_set.selected_product_tmpl_ids.ids,
        )

        # make sure filter active only for website_2
        self.assertIn(
            self.custom_value_filter_service.id,
            self.website_2.get_website_sale_custom_filters().ids,
        )
