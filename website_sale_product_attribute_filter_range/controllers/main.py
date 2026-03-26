# Copyright 2025 EthicHub
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import http
from odoo.http import request
from odoo.tools import float_round

from odoo.addons.website_sale.controllers.main import WebsiteSale


class WebsiteSaleAttributeRange(WebsiteSale):
    @staticmethod
    def _parse_attrib_ranges(attrib_ranges):
        """Parse attribute range query params.

        Format: ['attr_id-min-max', ...]
        Returns: {attr_id: (min_val, max_val)}
        """
        result = {}
        for item in attrib_ranges:
            parts = item.split("-", 2)
            if len(parts) != 3:
                continue
            try:
                attr_id = int(parts[0])
                min_val = float(parts[1]) if parts[1] else 0.0
                max_val = float(parts[2]) if parts[2] else 0.0
                result[attr_id] = (min_val, max_val)
            except ValueError:
                continue
        return result

    def _get_search_options(self, **kwargs):
        options = super()._get_search_options(**kwargs)
        options["attrib_range_dict"] = kwargs.get("attrib_range_dict", {})
        return options

    def _shop_get_query_url_kwargs(self, *args, **kwargs):
        result = super()._shop_get_query_url_kwargs(*args, **kwargs)
        result["attrib_range"] = kwargs.get("attrib_range", [])
        return result

    @http.route()
    def shop(
        self,
        page=0,
        category=None,
        search="",
        min_price=0.0,
        max_price=0.0,
        tags="",
        **post,
    ):
        # Parse range params before calling super so they flow through options
        request_args = request.httprequest.args
        attrib_ranges = request_args.getlist("attrib_range")
        attrib_range_dict = self._parse_attrib_ranges(attrib_ranges)

        if attrib_ranges:
            post["attrib_range"] = attrib_ranges
            post["attrib_range_dict"] = attrib_range_dict

        response = super().shop(
            page=page,
            category=category,
            search=search,
            min_price=min_price,
            max_price=max_price,
            tags=tags,
            **post,
        )

        if not hasattr(response, "qcontext"):
            return response

        # Compute available min/max for each range attribute
        ProductAttribute = request.env["product.attribute"]
        range_attributes = ProductAttribute.search(
            [
                ("display_type", "=", "range"),
                ("visibility", "=", "visible"),
            ]
        )

        range_data = {}
        AttribValue = request.env["product.attribute.value"]
        for attr in range_attributes:
            values = AttribValue.search(
                [("attribute_id", "=", attr.id), ("numeric_value", "!=", 0)]
            )
            if not values:
                continue
            numeric_values = values.mapped("numeric_value")
            available_min = float_round(min(numeric_values), 2)
            available_max = float_round(max(numeric_values), 2)
            if available_min == available_max:
                continue

            current_min, current_max = attrib_range_dict.get(attr.id, (0.0, 0.0))
            # Clamp values to available range
            if current_min and current_min > available_max:
                current_min = available_min
            if current_max and current_max < available_min:
                current_max = available_max

            range_data[attr.id] = {
                "attribute": attr,
                "available_min": available_min,
                "available_max": available_max,
                "current_min": current_min or available_min,
                "current_max": current_max or available_max,
                "step": attr.website_range_step or 0.5,
            }

        response.qcontext["range_filter_data"] = range_data
        response.qcontext["attrib_range_dict"] = attrib_range_dict

        # Exclude range attributes from the standard checkbox filter
        if range_attributes:
            attributes = response.qcontext.get("attributes")
            if attributes is not None:
                response.qcontext["attributes"] = attributes.filtered(
                    lambda a: a.id not in range_data
                )

        return response
