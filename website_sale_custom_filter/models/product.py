# Copyright 2022 Camptocamp SA
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html)

from odoo import api, models
from odoo.osv import expression


class ProductTemplate(models.Model):
    _inherit = "product.template"

    @api.model
    def _search_get_detail(self, website, order, options):
        """modify base domain based on modified filters"""
        res = super()._search_get_detail(website, order, options)
        original_domain = res["base_domain"][0]
        new_domain_elements = []

        if options.get("custom_checkbox_filters", False):
            checkbox_filter_domain = self._get_checkbox_filter_domain(
                options.get("custom_checkbox_filters")
            )
            if checkbox_filter_domain:
                new_domain_elements.append(checkbox_filter_domain)

        if options.get("custom_value_filters", False):
            value_filter_domain = self._get_value_filter_domain(
                options.get("custom_value_filters")
            )
            if value_filter_domain:
                new_domain_elements.append(value_filter_domain)
        if new_domain_elements:
            res["base_domain"][0] = expression.AND(
                [original_domain, new_domain_elements[0]]
            )
        return res

    def _get_checkbox_filter_domain(self, option_values):
        """get domain for checkbox filters"""
        subdomains = []
        CustomFilterValueObj = self.env["website.sale.custom.filter.value"]

        for _, val_id in option_values.items():
            filter_value = CustomFilterValueObj.browse(val_id)
            selected_products = filter_value.selected_product_tmpl_ids.ids
            if selected_products:
                subdomains.append([("id", "in", selected_products)])
        return expression.OR(subdomains)

    def _get_value_filter_domain(self, option_values):
        """build domain for numerical filter"""
        subdomains = []
        CustomFilterObj = self.env["website.sale.custom.filter"]

        for f_id, val_id in option_values.items():
            filter_id = CustomFilterObj.browse(int(f_id))
            filtering_field = filter_id.numerical_filter_field_id.name
            min_val = val_id.get("min_value", False)
            max_val = val_id.get("max_value", False)
            # build domain based on parameters
            if min_val and min_val != val_id["available_min_value"]:
                subdomains.append([(filtering_field, ">=", min_val)])
            if max_val and max_val != val_id["available_max_value"]:
                subdomains.append([(filtering_field, "<=", max_val)])
        return expression.AND(subdomains)
