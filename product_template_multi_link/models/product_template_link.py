# Copyright 2017-Today GRAP (http://www.grap.coop).
# @author Sylvain LE GAL <https://twitter.com/legalsylvain>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ProductTemplateLink(models.Model):
    _name = "product.template.link"
    _order = "product_template_id, linked_product_template_id"

    _LINK_TYPE_SELECTION = [("cross_sell", "Cross-Sell"), ("up_sell", "Up-Sell")]

    product_template_id = fields.Many2one(
        string="Source Product",
        comodel_name="product.template",
        required=True,
        ondelete="cascade",
    )

    product_template_image_small = fields.Binary(
        related="product_template_id.image_small"
    )

    linked_product_template_id = fields.Many2one(
        string="Linked Product",
        comodel_name="product.template",
        required=True,
        ondelete="cascade",
    )

    linked_product_template_image_small = fields.Binary(
        related="linked_product_template_id.image_small"
    )

    link_type = fields.Selection(
        string="Link Type",
        selection=_LINK_TYPE_SELECTION,
        required=True,
        default="cross_sell",
        help="* Cross-Sell : suggest your customer to"
        " purchase an additional product\n"
        "* Up-Sell : suggest your customer to purchase a higher-end product,"
        "  an upgrade, etc.",
    )

    sql_constraints = [
        (
            "template_link_uniq",
            "unique (product_template_id, linked_product_template_id, link_type)",
            "The products and the link type combination must be unique",
        )
    ]
