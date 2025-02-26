# Copyright 2015 Agile Business Group sagl (<http://www.agilebg.com>)
# Copyright 2017 Jairo Llopis <jairo.llopis@tecnativa.com>
# Copyright 2025 Carlos Lopez - Tecnativa
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.website_sale.controllers.main import WebsiteSale


class WebsiteSale(WebsiteSale):
    def _get_mandatory_billing_address_fields(self, country_sudo):
        field_names = super()._get_mandatory_billing_address_fields(country_sudo)
        if "vat" not in field_names:
            field_names |= {"vat"}
        return field_names

    def _prepare_address_form_values(
        self, *args, address_type, use_delivery_as_billing, **kwargs
    ):
        rendering_values = super()._prepare_address_form_values(
            *args,
            address_type=address_type,
            use_delivery_as_billing=use_delivery_as_billing,
            **kwargs,
        )
        rendering_values["show_vat"] = (
            address_type == "billing" or use_delivery_as_billing
        )
        return rendering_values
