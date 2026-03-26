# Copyright 2025 EthicHub
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    def _get_attribute_exclusions(
        self,
        parent_combination=None,
        parent_name=None,
        combination_ids=None,
    ):
        res = super()._get_attribute_exclusions(
            parent_combination=parent_combination,
            parent_name=parent_name,
            combination_ids=combination_ids,
        )
        range_ptav_ids = set(
            self.valid_product_template_attribute_line_ids.filtered(
                lambda ptal: ptal.attribute_id.display_type == "range"
            )
            .product_template_value_ids._only_active()
            .ids
        )
        if range_ptav_ids:
            str_ids = {str(pid) for pid in range_ptav_ids}
            for str_id in str_ids:
                res["exclusions"].pop(str_id, None)
                res["mapped_attribute_names"].pop(str_id, None)
            for key in list(res["exclusions"]):
                res["exclusions"][key] = [
                    v for v in res["exclusions"][key] if v not in range_ptav_ids
                ]
        return res

    def _get_combination_info(
        self,
        combination=False,
        product_id=False,
        add_qty=1.0,
        parent_combination=False,
        only_template=False,
    ):
        # Only extend an existing combination — never touch combination=False,
        # as super() uses that to trigger _get_first_possible_combination().
        if combination:
            range_lines = self.valid_product_template_attribute_line_ids.filtered(
                lambda ptal: ptal.attribute_id.display_type == "range"
            )
            for ptal in range_lines:
                active_ptavs = ptal.product_template_value_ids._only_active()
                if active_ptavs and not combination & active_ptavs:
                    combination |= active_ptavs[:1]
        return super()._get_combination_info(
            combination,
            product_id=product_id,
            add_qty=add_qty,
            parent_combination=parent_combination,
            only_template=only_template,
        )

    @api.model
    def _search_get_detail(self, website, order, options):
        result = super()._search_get_detail(website, order, options)
        attrib_range_dict = options.get("attrib_range_dict")
        if attrib_range_dict:
            AttribValue = self.env["product.attribute.value"]
            for attribute_id, (min_val, max_val) in attrib_range_dict.items():
                domain = [("attribute_id", "=", attribute_id)]
                if min_val:
                    domain.append(("numeric_value", ">=", min_val))
                if max_val:
                    domain.append(("numeric_value", "<=", max_val))
                value_ids = AttribValue.search(domain).ids
                if value_ids:
                    result["base_domain"].append(
                        [("attribute_line_ids.value_ids", "in", value_ids)]
                    )
        return result
