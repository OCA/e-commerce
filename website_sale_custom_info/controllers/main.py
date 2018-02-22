# -*- coding: utf-8 -*-
# Copyright 2016 Jairo Llopis <jairo.llopis@tecnativa.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from openerp.addons.website_sale.controllers.main import website_sale
from openerp.http import request, route


class WebsiteSale(website_sale):
    def _get_custom_info(self):
        """Get custom info parameters in a list."""
        for key, values in request.httprequest.args.iterlists():
            for value in values:
                if key.startswith("custom_info,") and value:
                    operator, prop = key.split(",")[1:]
                    yield int(prop), operator, value

    def _get_search_domain(self, search, category, attrib_values,
                           apply_custom_info=True):
        result = super(WebsiteSale, self)._get_search_domain(
            search, category, attrib_values)
        if apply_custom_info:
            Value = request.env["custom.info.value"]
            domains = dict()
            for prop, operator, value in self._get_custom_info():
                # Search all values with this criteria
                records = Value.search([
                    ("property_id", "=", prop),
                    ("value", operator, value),
                ])
                domains.setdefault((prop, operator), list())
                domains[(prop, operator)].append(
                    ("custom_info_ids", "in", records.ids))
            # Join several critera for same property by OR
            for domain in domains.values():
                result += ["|"] * (len(domain) - 1) + domain
        return result

    @route()
    def shop(self, page=0, category=None, search='', ppg=False, **post):
        result = super(WebsiteSale, self).shop(
            page, category, search, ppg, **post)
        custom_info = list()
        custom_info_posted = set(self._get_custom_info())

        # Get information from parent method that it does not expose
        attrib_list = request.httprequest.args.getlist('attrib')
        attrib_values = [map(int, v.split("-")) for v in attrib_list if v]
        all_products = request.env["product.template"].search(
            self._get_search_domain(
                search, category, attrib_values, apply_custom_info=False))
        filtered_products = request.env["product.template"].search(
            self._get_search_domain(
                search, category, attrib_values))
        for prop in filtered_products.mapped("custom_info_ids.property_id"):
            if not prop.product_public_filter:
                continue
            ci = {
                "property": prop,
            }
            if prop.field_type == "str":
                ci["value"] = post.get(
                    "custom_info,ilike,{}".format(prop.id), False)
            else:
                values = request.env["custom.info.value"].search([
                    ("property_id", "=", prop.id),
                    ("res_id", "in", all_products.ids),
                    ("value", "!=", False),
                    ("value", "!=", ""),
                ])
                if prop.field_type in {"int", "float"}:
                    # Load from SQL to boost performance
                    request.cr.execute(
                        """SELECT MIN(value_{0}) as min, MAX(value_{0}) as max
                           FROM {1}
                           WHERE id IN %s""".format(prop.field_type,
                                                    values._table),
                        (tuple(values.ids),)
                    )
                    ci["range"] = request.cr.dictfetchone()
                    ci["range"].update({
                        "from": post.get(
                            "custom_info,>=,{}".format(prop.id), ""),
                        "to": post.get(
                            "custom_info,<=,{}".format(prop.id), ""),
                    })
                else:
                    ci["options"] = sorted(set(values.mapped("value")))
                    # Skip selectables without options
                    if not ci["options"]:
                        continue
            custom_info.append(ci)

        result.qcontext.update({
            "custom_info": custom_info,
            "custom_info_posted": custom_info_posted,
        })
        return result
