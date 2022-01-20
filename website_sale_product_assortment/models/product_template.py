# Copyright 2021 Tecnativa - Carlos Roca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    @api.model
    def get_product_assortment_restriction_info(self, product_ids):
        partner = self.env.user.partner_id
        website = self.env["website"].get_current_website()
        assortments = (
            self.env["ir.filters"]
            .sudo()
            .search(
                [
                    ("is_assortment", "=", True),
                    ("website_availability", "in", ["no_purchase", "no_show"]),
                    "|",
                    ("website_ids", "=", website.id),
                    ("website_ids", "=", False),
                ]
            )
        )
        assortment_dict = {}
        for assortment in assortments:
            if partner & assortment.with_context(active_test=False).all_partner_ids:
                allowed_product_ids = assortment.all_product_ids.ids
                for product in product_ids:
                    if product not in allowed_product_ids:
                        assortment_dict.setdefault(product, self.env["ir.filters"])
                        assortment_dict[product] |= assortment
        return assortment_dict

    def _get_combination_info(
        self,
        combination=False,
        product_id=False,
        add_qty=1,
        pricelist=False,
        parent_combination=False,
        only_template=False,
    ):
        res = super()._get_combination_info(
            combination=combination,
            product_id=product_id,
            add_qty=add_qty,
            pricelist=pricelist,
            parent_combination=parent_combination,
            only_template=only_template,
        )
        product_res_id = res["product_id"]
        if self.env.context.get("website_id") and not only_template and product_res_id:
            not_allowed_product_dict = self.get_product_assortment_restriction_info(
                [product_res_id]
            )
            if not_allowed_product_dict and product_res_id in not_allowed_product_dict:
                res["product_avoid_purchase"] = True
                res["product_assortment_type"] = "no_purchase"
                assortments = not_allowed_product_dict[product_res_id]
                for assortment in assortments:
                    if assortment.website_availability == "no_show":
                        res["product_assortment_type"] = "no_show"
                        break
                if res["product_assortment_type"] != "no_show":
                    assortment = assortments[0]
                    res["message_unavailable"] = assortment.message_unavailable
                    res["assortment_information"] = assortment.assortment_information
            else:
                res["product_avoid_purchase"] = False
        return res
