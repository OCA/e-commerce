# Copyright 2021 Tecnativa - Jairo Llopis
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import timedelta

from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    resource_booking_timeout = fields.Float(
        "Pre-booking timeout",
        compute="_compute_resource_booking_timeout",
        inverse="_set_resource_booking_timeout",
        search="_search_resource_booking_timeout",
        help=(
            "When resources are pre-booked, the booking will expire after "
            "this timeout if the quotation is not confirmed in time."
        ),
    )
    resource_booking_expiration = fields.Datetime(
        compute="_compute_resource_booking_expiration"
    )

    def _get_related_fields_variant_template(self):
        res = super()._get_related_fields_variant_template()
        return res + ["resource_booking_timeout"]

    @api.model_create_multi
    def create(self, vals_list):
        templates = super().create(vals_list)
        for template, vals in zip(templates, vals_list):
            if (
                "resource_booking_timeout" in vals
                and len(template.product_variant_ids) == 1
            ):
                template.product_variant_ids.resource_booking_timeout = vals[
                    "resource_booking_timeout"
                ]
        return templates

    @api.depends("product_variant_ids.resource_booking_timeout")
    def _compute_resource_booking_timeout(self):
        self._compute_template_field_from_variant_field("resource_booking_timeout")

    def _set_resource_booking_timeout(self):
        self._set_product_variant_field("resource_booking_timeout")

    def _search_resource_booking_timeout(self, operator, value):
        return [("product_variant_ids.resource_booking_timeout", operator, value)]

    @api.depends("resource_booking_type_id", "resource_booking_timeout")
    def _compute_resource_booking_expiration(self):
        """When would the booking expire if placed right now."""
        now = fields.Datetime.now()
        for one in self:
            if not one.resource_booking_type_id:
                one.resource_booking_expiration = False
            else:
                one.resource_booking_expiration = now + timedelta(
                    hours=one.resource_booking_timeout or 0
                )
