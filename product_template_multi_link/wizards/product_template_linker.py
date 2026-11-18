# Copyright 2020 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models


class ProductTemplateLinker(models.TransientModel):
    """
    Wizard used to link product template together in one shot
    """

    _name = "product.template.linker"
    _description = "Product template linker wizard"

    operation_type = fields.Selection(
        selection=[
            ("unlink", "Remove existing links"),
            ("link", "Link these products"),
        ],
        string="Operation",
        required=True,
        help="Remove existing links: will remove every existing link "
        "on each selected products;\n"
        "Link these products: will link all selected "
        "products together.",
    )
    product_ids = fields.Many2many(
        comodel_name="product.template",
        string="Products",
    )
    type_id = fields.Many2one(
        string="Link type",
        comodel_name="product.template.link.type",
        ondelete="restrict",
    )

    @api.model
    def default_get(self, fields_list):
        """Inherit default_get to auto-fill product_ids with current context

        :param fields_list: list of str
        :return: dict
        """
        result = super().default_get(fields_list)
        ctx = self.env.context
        active_ids = ctx.get("active_ids", ctx.get("active_id", []))
        products = []
        if ctx.get("active_model") == self.product_ids._name and active_ids:
            products = [(6, False, list(active_ids))]
        result.update(
            {
                "product_ids": products,
            }
        )
        return result

    def action_apply(self):
        if self.operation_type == "link":
            self.action_apply_link()
        elif self.operation_type == "unlink":
            self.action_apply_unlink()
        return {}

    def action_apply_unlink(self):
        """Remove links from products.

        :return: product.template.link recordset
        """
        self.product_ids.mapped("product_template_link_ids").unlink()
        return self.env["product.template.link"].browse()

    def action_apply_link(self):
        """Add link to products.

        :return: product.template.link recordset
        """
        links = self.env["product.template.link"].browse()
        for product in self.product_ids:
            existing_links = product.product_template_link_ids.filtered(
                lambda r: r.type_id == self.type_id
            )
            linked_products = existing_links.mapped(
                "left_product_tmpl_id"
            ) | existing_links.mapped("right_product_tmpl_id")
            products_to_link = self.product_ids - linked_products - product
            links |= self._create_link(product, products_to_link)
        return links

    def _create_link(self, product_source, target_products):
        """Create the link between given product source and target products.

        :param product_source: product.template recordset
        :param target_products: product.template recordset
        :return: product.template.link recordset
        """
        self.ensure_one()
        prod_link_obj = self.env["product.template.link"]
        product_links = prod_link_obj.browse()
        for target_product in target_products:
            values = {
                "left_product_tmpl_id": product_source.id,
                "right_product_tmpl_id": target_product.id,
                "type_id": self.type_id.id,
            }
            product_links |= prod_link_obj.create(values)
        return product_links
