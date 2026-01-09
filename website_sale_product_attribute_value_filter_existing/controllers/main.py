# Copyright 2019 Tecnativa - Sergio Teruel
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from odoo.http import request

from odoo.addons.website_sale.controllers.main import WebsiteSale


class ProductAttributeValues(WebsiteSale):
    def _get_additional_shop_values(self, values, **post):
        res = super()._get_additional_shop_values(values, **post)
        search_product = values.get("search_product")
        attributes = values.get("attributes")
        if search_product and attributes:
            ProductTemplateAttributeLine = request.env[
                "product.template.attribute.line"
            ]
            lines = ProductTemplateAttributeLine.search_read(
                domain=[
                    ("product_tmpl_id", "in", search_product.ids),
                    ("attribute_id", "in", attributes.ids),
                    ("attribute_id.visibility", "=", "visible"),
                ],
                fields=["value_ids"],
            )
            used_value_ids = {
                value_id for line in lines for value_id in line.get("value_ids", [])
            }
            res["attr_values_used_ids"] = used_value_ids
        return res
