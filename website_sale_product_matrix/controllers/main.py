# Copyright 2025 Tecnativa - David Vidal
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from werkzeug.exceptions import NotFound

from odoo.exceptions import UserError
from odoo.http import request, route

from odoo.addons.website_sale.controllers.cart import Cart
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.addons.website_sale.controllers.product_configurator import (
    WebsiteSaleProductConfiguratorController,
)


class WebsiteSaleProductMatrix(WebsiteSale):
    @route(
        ["/shop/cart/update_from_matrix"],
        type="http",
        auth="public",
        methods=["POST"],
        website=True,
    )
    def cart_update_from_matrix(self, product_template_id, grid, **kw):
        """This route is called when adding a product to cart from the product matrix"""
        sale_order = request.cart or request.website._create_cart()
        sale_order.update(
            {
                "grid_product_tmpl_id": int(product_template_id),
                "grid_update": True,
                "grid": grid,
            }
        )
        sale_order._apply_grid()
        # Refresh the quantity of the cart shown in the header
        sale_order._verify_cart_after_update()
        return request.redirect("/shop/cart")


class WebsiteSaleProductMatrixConfigurator(WebsiteSaleProductConfiguratorController):
    @route(
        "/website_sale_product_matrix/get_matrix",
        type="jsonrpc",
        auth="public",
        website=True,
        readonly=True,
    )
    def website_sale_product_matrix_get_matrix(self, product_template_id):
        """Return the matrix of a product to fill it in the product configurator.

        It's rendered with the same template as in the product page.
        """
        product_template = (
            request.env["product.template"].browse(int(product_template_id)).exists()
        )
        if not product_template or product_template.product_add_mode != "matrix":
            raise NotFound()
        matrix = self._get_product_matrix(product_template)
        html = request.env["ir.ui.view"]._render_template(
            "website_sale_product_matrix.product_matrix",
            {"product_matrix": matrix, "product_configurator": True},
        )
        return {"html": html, "matrix": matrix["matrix"]}

    def _get_product_matrix(self, product_template):
        """Return the matrix of a product filled in with the quantities in the cart.

        As in the product page, the matrix sets the quantities of the cart. Each
        cell is completed with the variant name and price to show the configured
        lines in the configurator. The name goes in another key, as `name` is what
        tells apart the row headers.
        """
        if request.cart:
            matrix = request.cart._get_matrix(product_template)
        else:
            matrix = product_template._get_template_matrix(
                company_id=request.website.company_id,
                currency_id=request.website.currency_id,
                display_extra_price=True,
            )
        Ptav = request.env["product.template.attribute.value"]
        for row in matrix["matrix"]:
            for cell in row:
                if not cell.get("is_possible_combination"):
                    continue
                combination = Ptav.browse(cell["ptav_ids"])
                combination_info = product_template._get_combination_info(combination)
                cell.update(
                    {
                        "combination_name": combination._get_combination_name(),
                        "unit_price": combination_info["price"],
                    }
                )
        return matrix

    def _get_product_information(self, product_template, *args, **kwargs):
        values = super()._get_product_information(product_template, *args, **kwargs)
        if request.is_frontend and product_template.product_add_mode == "matrix":
            # The variants are chosen in the matrix, not the selected combination
            matrix = self._get_product_matrix(product_template)
            values.update(
                {
                    "display_name": product_template.display_name,
                    "is_matrix": True,
                    "matrix_lines": [
                        {
                            "ptav_ids": cell["ptav_ids"],
                            "qty": cell["qty"],
                            "name": cell["combination_name"],
                            "unit_price": cell["unit_price"],
                        }
                        for row in matrix["matrix"]
                        for cell in row
                        if cell.get("is_possible_combination") and cell.get("qty")
                    ],
                }
            )
        return values


class WebsiteSaleProductMatrixCart(Cart):
    @route()
    def add_to_cart(
        self,
        product_template_id,
        product_id,
        quantity=1.0,
        linked_products=None,
        matrix_changes=None,
        **kwargs,
    ):
        """Set the variants filled in the matrix of the product configurator.

        As in the product page, the matrix sets the quantities of the product in
        the cart, so only the difference is added and the variants left out are
        removed. The lines are matched as in the product page, that is, also the
        ones with custom attribute values. The optional products are linked to the
        first updated variant.
        """
        if not matrix_changes:
            return super().add_to_cart(
                product_template_id,
                product_id,
                quantity=quantity,
                linked_products=linked_products,
                **kwargs,
            )
        # They belong to the combination selected in the configurator, which
        # isn't used, as each variant has its own one.
        kwargs.pop("no_variant_attribute_value_ids", None)
        kwargs.pop("product_custom_attribute_values", None)
        order_sudo = request.cart or request.website._create_cart()
        product_template = request.env["product.template"].browse(
            int(product_template_id)
        )
        Ptav = request.env["product.template.attribute.value"]
        variants = []
        for change in matrix_changes:
            combination = Ptav.browse(change["ptav_ids"]).exists()
            product = (
                combination.product_tmpl_id == product_template
                and product_template.sudo()._create_product_variant(combination)
            )
            if not product:
                raise UserError(
                    request.env._(
                        "The given product does not exist therefore it cannot be "
                        "added to cart."
                    )
                )
            no_variant_combination = (
                combination - combination._without_no_variant_attributes()
            )
            variants.append((product, no_variant_combination, int(change["qty"])))
        kept_lines = {
            (product, no_variant_combination)
            for product, no_variant_combination, qty in variants
            if qty > 0
        }
        matrix_lines = order_sudo.order_line.filtered(
            lambda line: line.product_template_id == product_template
            and not line.combo_item_id
        )
        removed_lines = matrix_lines.filtered(
            lambda line: (line.product_id, line.product_no_variant_attribute_value_ids)
            not in kept_lines
        )
        for line in removed_lines:
            order_sudo._cart_update_line_quantity(line.id, 0)
        matrix_lines -= removed_lines
        result = {}
        for product, no_variant_combination, qty in variants:
            if qty <= 0:
                continue
            lines = matrix_lines.filtered(
                lambda line, product=product, pnav=no_variant_combination: (
                    line.product_id == product
                    and line.product_no_variant_attribute_value_ids == pnav
                )
            )
            diff = qty - sum(lines.mapped("product_uom_qty"))
            if len(lines) > 1 and diff:
                raise UserError(
                    request.env._(
                        "You cannot change the quantity of a product present in "
                        "multiple sale lines."
                    )
                )
            if diff <= 0 and (result or not linked_products):
                # Nothing added to notify, unless the optional products are
                # linked to it.
                if diff:
                    order_sudo._cart_update_line_quantity(lines.id, qty)
                continue
            # The line to update is given, as the ones with custom attribute
            # values wouldn't be found.
            request.cart = order_sudo.with_context(
                website_sale_product_matrix_line_id=lines.id
            )
            try:
                values = super().add_to_cart(
                    product_template_id,
                    product.id,
                    quantity=diff,
                    no_variant_attribute_value_ids=no_variant_combination.ids,
                    linked_products=not result and linked_products or None,
                    **kwargs,
                )
            finally:
                request.cart = order_sudo
            if not result:
                result = values
                continue
            notification_info = result["notification_info"]
            notification_info.setdefault("lines", []).extend(
                values["notification_info"].get("lines", [])
            )
            notification_info.setdefault(
                "currency_id", values["notification_info"].get("currency_id")
            )
            notification_info["warning"] = "\n".join(
                filter(
                    None,
                    [
                        notification_info.get("warning"),
                        values["notification_info"].get("warning"),
                    ],
                )
            )
            result["tracking_info"] += values["tracking_info"]
            result["quantity"] += values["quantity"]
        if not result:
            result = {"notification_info": {}, "quantity": 0, "tracking_info": []}
        # The lines reduced after adding the first variant change it too
        result["cart_quantity"] = order_sudo.cart_quantity
        return result
