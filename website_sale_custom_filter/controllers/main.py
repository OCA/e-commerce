# Copyright 2022 Camptocamp
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.http import request

from odoo.addons.website_sale.controllers.main import WebsiteSale


class WebsiteSale(WebsiteSale):

    # get min & max from url params for range widgets only
    def get_min_max_custom_filters(self):
        req = dict(request.httprequest.args)
        min_max_filter_vals = {}
        for vals in req.get("min_cust_filter", "").split(","):
            if vals:
                f_id, f_min_val = vals.split("_")
                f_id = int(f_id)
                f_min_val = int(f_min_val)
                if not min_max_filter_vals.get(f_id, False):
                    min_max_filter_vals[f_id] = {"min": f_min_val}
                else:
                    min_max_filter_vals[f_id]["min"] = f_min_val
        for vals in req.get("max_cust_filter", "").split(","):
            if vals:
                f_id, f_max_val = vals.split("_")
                f_max_val = int(f_max_val)
                if not min_max_filter_vals.get(f_id, False):
                    min_max_filter_vals[f_id] = {"max": f_max_val}
                else:
                    min_max_filter_vals[f_id]["max"] = f_max_val
        return min_max_filter_vals

    def get_custom_checkbox_filter_values(self):
        req = dict(request.httprequest.args)
        value_filter_data = {}
        for data in req.get("cust_filter", "").split("&"):
            if data:
                f_id, val = data.split("-")
                if f_id in value_filter_data.keys():
                    value_filter_data[f_id].append(int(val))
                else:
                    value_filter_data[f_id] = [int(val)]
        return value_filter_data

    def _prepare_filter_actual_website_values(self, min_max_values):
        values = {}
        if min_max_values.get("min"):
            values["min_value"] = min_max_values["min"]
        if min_max_values.get("max"):
            values["max_value"] = min_max_values["max"]
        return values

    def get_custom_range_filter_values(self):
        range_filter_data = {}
        cust_filter_min_max_vals = self.get_min_max_custom_filters()
        curr_website = request.env["website"].get_current_website()
        numerical_filters_available_on_website = request.env[
            "website.sale.custom.filter"
        ].search(
            [("website_ids", "in", curr_website.id), ("filter_type", "=", "numerical")]
        )

        for num_filter in numerical_filters_available_on_website:
            curr_filter_id = num_filter.id
            range_filter_data[curr_filter_id] = {}
            range_filter_data[curr_filter_id].update(
                num_filter._prepare_filter_default_website_values()
            )
            if cust_filter_min_max_vals:
                range_filter_data[curr_filter_id].update(
                    self._prepare_filter_actual_website_values(
                        cust_filter_min_max_vals.get(curr_filter_id)
                    )
                )
        return range_filter_data

    def _get_additional_shop_values(self, values):
        res = super()._get_additional_shop_values(values)
        custom_product_filters_enabled = request.website.is_view_active(
            "website_sale_custom_filter.products_filters"
        )
        if custom_product_filters_enabled:
            # get values from custom range filters
            values["filter_vals"] = self.get_custom_range_filter_values()
            # get values for custom checkbox filters
            values["custom_checkbox_filters"] = self.get_custom_checkbox_filter_values()
            # check if any custom filter changed so we use
            # it as condition to show "clean filter" btn
            values["custom_val_filter_changed"] = any(
                [
                    i in request.httprequest.args
                    for i in ["cust_filter", "min_cust_filter", "max_cust_filter"]
                ]
            )
            res.update(values)
        return res

    # override _get_search_options to include chosen filters values
    def _get_search_options(
        self,
        category=None,
        attrib_values=None,
        pricelist=None,
        min_price=0.0,
        max_price=0.0,
        conversion_rate=1,
        **post,
    ):
        res = super()._get_search_options(
            category,
            attrib_values,
            pricelist,
            min_price,
            max_price,
            conversion_rate,
            **post,
        )
        res["custom_checkbox_filters"] = self.get_custom_checkbox_filter_values()
        res["custom_value_filters"] = self.get_custom_range_filter_values()
        return res
