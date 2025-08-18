from odoo import fields, models

from ..helpers import get_active_saleor_account


class SaleorProductType(models.Model):
    _name = "saleor.product.type"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Saleor Product Type"

    name = fields.Char(required=True)
    slug = fields.Char()
    kind = fields.Selection(
        selection=[
            ("normal", "Regular product type"),
            ("gift_card", "Gift card product type"),
        ],
        required=True,
        default="normal",
    )
    tax_id = fields.Many2one(
        "account.tax",
        domain=[("type_tax_use", "=", "sale")],
    )
    product_attribute_ids = fields.Many2many(
        "product.attribute",
        "saleor_product_type_product_attribute_rel",
        "product_type_id",
        "attribute_id",
        string="Product Attributes",
        domain=[("saleor_attribute_id", "!=", False)],
    )
    use_variant_attributes = fields.Boolean(
        string="Product type uses Variant Attributes",
        default=False,
        help="Product type uses Variant Attributes",
    )
    variant_attribute_ids = fields.Many2many(
        "product.attribute",
        "saleor_product_type_variant_attribute_rel",
        "product_type_id",
        "variant_attribute_id",
        string="Variant Attributes",
        domain=[("saleor_attribute_id", "!=", False)],
    )
    is_shipping = fields.Boolean(
        string="Is This Product Shippable?",
        default=False,
    )
    weight = fields.Float(
        default=0,
    )
    metadata_line = fields.One2many(
        "product.type.meta.line",
        "product_type_id",
    )
    private_metadata_line = fields.One2many(
        "product.type.private.meta.line",
        "product_type_id",
    )
    saleor_product_type_id = fields.Char(copy=False)

    _sql_constraints = [
        (
            "saleor_product_type_slug_unique",
            "unique(slug)",
            "Saleor slug must be unique on product types.",
        )
    ]

    def write(self, vals):
        res = super().write(vals)
        account = get_active_saleor_account(self.env, raise_if_missing=False)
        if account:
            for rec in self:
                try:
                    account.sync_product_type_from_ptype(rec)
                except Exception:
                    continue
        return res
