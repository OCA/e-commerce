# Copyright 2025 Kencove (https://www.kencove.com/)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import _, api, fields, models

from ..helpers import (
    apply_reward_mapping,
    build_catalogue_predicate,
    compute_merged_description_editorjs,
)


class DiscountRule(models.Model):
    _name = "discount.rule"
    _description = "Discount Rule"

    name = fields.Char(required=True)
    channel_id = fields.Many2one("saleor.channel", required=True)
    program_id = fields.Many2one(
        "loyalty.program",
        string="Loyalty Program",
        ondelete="cascade",
    )
    predicate_type = fields.Selection(related="program_id.discount_type", readonly=True)
    condition_ids = fields.One2many(
        "discount.rule.condition", "discount_rule_id", string="Conditions"
    )
    reward_type = fields.Selection(
        selection=[
            ("gift", "Gift"),
            ("sub", "Subtotal discount"),
        ],
        default="sub",
    )
    reward_unit = fields.Selection(
        selection=[
            ("percent", "%"),
            ("currency", "Currency"),
        ],
        required=True,
        default="percent",
    )
    display_unit = fields.Char()
    reward_value = fields.Float()
    description = fields.Html(string="Description (HTML)")
    duplicate_type_warning = fields.Text(compute="_compute_duplicate_type_warning")

    # Saleor linkage
    saleor_promotion_rule_id = fields.Char(
        string="Saleor Promotion Rule ID",
        copy=False,
        index=True,
        help="ID of this rule in Saleor",
    )

    @api.onchange("reward_unit")
    def _compute_display_unit(self):
        for line in self:
            if line.reward_unit == "currency":
                line.display_unit = line.channel_id.currency_id.name or ""
            elif line.reward_unit == "percent":
                line.display_unit = "%"
            else:
                line.display_unit = ""

    @api.depends("condition_ids.catalogue_predicate_type")
    def _compute_duplicate_type_warning(self):
        for rule in self:
            warning = ""
            types = rule.condition_ids.mapped("catalogue_predicate_type")
            duplicates = [t for t in set(types) if t and types.count(t) > 1]

            if duplicates:
                sel = (
                    self.env["discount.rule.condition"]
                    ._fields["catalogue_predicate_type"]
                    .selection
                )
                labels = [dict(sel).get(t) for t in duplicates if t]
                labels = [lbl for lbl in labels if isinstance(lbl, str)]
                warning = _(
                    "Warning: Rule '%(rule)s' has duplicate condition types: %(types)s.",
                    {
                        "rule": rule.display_name,
                        "types": ", ".join(labels),
                    },
                )
            rule.duplicate_type_warning = warning

    # --- Saleor helpers ---
    def _saleor_prepare_rule_input(self):
        self.ensure_one()
        # Minimal compatible input: promotion, name, optional description
        input_data = {
            "name": self.name or "",
        }

        # Description via helpers
        desc = compute_merged_description_editorjs(
            self.description or "",
            [
                c.description
                for c in self.condition_ids
                if getattr(c, "description", None)
            ],
        )
        if desc is not None:
            input_data["description"] = desc

        # Catalogue predicate via helpers
        if self.predicate_type == "catalogue":
            input_data["cataloguePredicate"] = build_catalogue_predicate(
                self.condition_ids, self.env
            )

        # Reward mapping via helpers
        apply_reward_mapping(
            input_data, self.reward_type, self.reward_unit, self.reward_value
        )
        return input_data
