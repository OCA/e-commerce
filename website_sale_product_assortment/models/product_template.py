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
        assortments = assortments.filtered(
            lambda x: partner & x.with_context(active_test=False).all_partner_ids
        )
        if not assortments:
            return assortments, []
        # if there are multiple assortments for the same partner
        # the allowed products are all the products present in
        # at least one assortment (OR logic)
        allowed_product_ids = assortments.all_product_ids.ids
        restricted_product_ids = {
            x for x in product_ids if x not in allowed_product_ids
        }
        return assortments, restricted_product_ids

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
            (
                assortments,
                restricted_product_ids,
            ) = self.get_product_assortment_restriction_info([product_res_id])
            if restricted_product_ids and product_res_id in restricted_product_ids:
                res["product_avoid_purchase"] = True
                if any(a.website_availability == "no_show" for a in assortments):
                    res["product_assortment_type"] = "no_show"
                else:
                    res["product_assortment_type"] = "no_purchase"
                    asrtm = assortments.filtered("message_unavailable")
                    if asrtm:
                        res["message_unavailable"] = asrtm[0].message_unavailable
                    asrtm = assortments.filtered("assortment_information")
                    if asrtm:
                        res["assortment_information"] = asrtm[0].assortment_information
            else:
                res["product_avoid_purchase"] = False
        return res
