# Copyright 2025 Kencove (https://www.kencove.com/)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class DiscountRuleCondition(models.Model):
    _name = "discount.rule.condition"
    _description = "Discount Rule Condition"

    discount_rule_id = fields.Many2one(
        "discount.rule",
        string="Discount Rule",
        ondelete="cascade",
    )
    predicate_type = fields.Selection(
        related="discount_rule_id.predicate_type",
        readonly=True,
    )
    catalogue_predicate_type = fields.Selection(
        selection=[
            ("product", "Product"),
            ("collection", "Collection"),
            ("variant", "Variant"),
            ("category", "Category"),
        ],
    )
    order_predicate_type = fields.Selection(
        selection=[
            ("subtotal", "Subtotal Price"),
            ("total", "Total Price"),
        ],
    )
    operator_id = fields.Many2one(
        "condition.operation.type",
        string="Operator",
    )
    program_id = fields.Many2one(
        related="discount_rule_id.program_id",
        store=True,
    )

    # Catalogue target selections
    product_template_ids = fields.Many2many(
        "product.template",
        "discount_rule_condition_product_template_rel",
        "condition_id",
        "product_tmpl_id",
        string="Products",
    )
    product_variant_ids = fields.Many2many(
        "product.product",
        "discount_rule_condition_product_variant_rel",
        "condition_id",
        "product_id",
        string="Variants",
    )
    product_collection_ids = fields.Many2many(
        "product.collection",
        "discount_rule_condition_product_collection_rel",
        "condition_id",
        "collection_id",
        string="Collections",
    )
    product_category_ids = fields.Many2many(
        "product.category",
        "discount_rule_condition_product_category_rel",
        "condition_id",
        "category_id",
        string="Categories",
    )

    # Optional human description shown in Saleor (merged into rule description)
    description = fields.Html(string="Condition Description (HTML)")

    @api.onchange("catalogue_predicate_type")
    def _onchange_catalogue_predicate_type(self):
        """Clear values of fields not matching the current type"""
        if self.catalogue_predicate_type != "product":
            self.product_template_ids = [(5, 0, 0)]
        if self.catalogue_predicate_type != "variant":
            self.product_variant_ids = [(5, 0, 0)]
        if self.catalogue_predicate_type != "collection":
            self.product_collection_ids = [(5, 0, 0)]
        if self.catalogue_predicate_type != "category":
            self.product_category_ids = [(5, 0, 0)]

    @api.constrains("catalogue_predicate_type")
    def _check_catalogue_predicate_type_not_empty(self):
        for rec in self:
            if not rec.catalogue_predicate_type:
                raise ValidationError(
                    _(
                        "Condition type cannot be empty."
                        " Please select a Catalogue Predicate Type."
                    )
                )
