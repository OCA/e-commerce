# Copyright 2026 Camptocamp SA
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from markupsafe import Markup

from odoo import api, fields, models

VARIANT_MODEL = "product.product"

EXTRA_FIELD_MODELS = ["product.template", "product.product"]

EXTRA_FIELD_TTYPES = [
    "char",
    "binary",
    "integer",
    "float",
    "date",
    "datetime",
    "selection",
    "many2one",
    "one2many",
    "many2many",
]


class WebsiteSaleExtraField(models.Model):
    _inherit = "website.sale.extra.field"

    field_id = fields.Many2one(
        domain=[
            ("model_id.model", "in", EXTRA_FIELD_MODELS),
            ("ttype", "in", EXTRA_FIELD_TTYPES),
        ],
    )
    is_variant_field = fields.Boolean(compute="_compute_is_variant_field")

    @api.depends("field_id.model_id.model")
    def _compute_is_variant_field(self):
        for extra_field in self:
            extra_field.is_variant_field = (
                extra_field.field_id.sudo().model_id.model == VARIANT_MODEL
            )

    def _get_source_record(self, product, product_variant):
        """Return the record the extra field value must be read from.

        Variant scoped fields are read from the currently displayed variant,
        template scoped ones from the product template.
        """
        self.ensure_one()
        return product_variant if self.is_variant_field else product

    def _get_render_options(self):
        """Return the ``t-options`` used to render the extra field value."""
        self.ensure_one()
        field_id = self.field_id.sudo()
        ttype = field_id.ttype
        options = {"widget": ttype}
        field = self.env[field_id.model_id.model]._fields.get(self.name)
        if not field:
            return options
        if ttype == "float":
            # Without an explicit precision, `ir.qweb.field.float` falls back to
            # a significant digits heuristic instead of the decimal precision
            # configured on the field.
            digits = field.get_digits(self.env)
            if digits:
                options["precision"] = digits[1]
        elif ttype == "selection":
            # `ir.qweb.field.selection` requires the labels mapping, which is
            # only injected automatically when rendering a record, not a value.
            options["selection"] = dict(field.get_description(self.env)["selection"])
        return options

    def _get_converter(self):
        """Return the ``ir.qweb.field`` model rendering the extra field value.

        Some field types have no dedicated converter, QWeb falls back on the
        base one for them.
        """
        self.ensure_one()
        model = f"ir.qweb.field.{self.field_id.sudo().ttype}"
        return self.env[model] if model in self.env else self.env["ir.qweb.field"]

    def _render_value(self, record):
        """Return the HTML rendering of the extra field value on ``record``."""
        self.ensure_one()
        if not record:
            return ""
        value = record.sudo()[self.name]
        if not value:
            return ""
        field_id = self.field_id.sudo()
        if field_id.ttype == "binary":
            return Markup(
                '<a target="_blank" href="/web/content/%s/%s/%s?download=1">'
                '<i class="fa fa-file"/></a>'
            ) % (field_id.model_id.model, record.id, self.name)
        rendered = self._get_converter().value_to_html(
            value, self._get_render_options()
        )
        return Markup(rendered) if rendered else ""

    def _get_rendered_values(self, record):
        """Return ``{field name: rendered value}`` for every field of ``self``."""
        return {
            extra_field.name: extra_field._render_value(record) for extra_field in self
        }

    def _has_content_to_display(self, product, product_variant):
        """Whether the extra fields block must be rendered for that product.

        Variant scoped fields always reserve their place in the page: their value
        is refreshed client side when the customer selects another variant, so an
        empty value on the variant displayed first must not remove the block.
        """
        return any(
            extra_field.is_variant_field
            or extra_field._render_value(
                extra_field._get_source_record(product, product_variant)
            )
            for extra_field in self
        )
