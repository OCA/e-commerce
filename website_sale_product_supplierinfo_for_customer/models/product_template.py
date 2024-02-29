from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    partner_price = fields.Float(
        "Partner Price", compute="_compute_partner_price", digits="Product Price"
    )

    @api.depends("list_price")
    @api.depends_context("partner", "partner_id", "user")
    def _compute_partner_price(self):
        for template in self:
            template.partner_price = (
                template.product_variant_id.price_compute("partner")[
                    template.product_variant_id.id
                ]
                or template.list_price
            )

    def _get_customerinfo_name(self, partner, product=False):
        if self.customer_ids:
            if not isinstance(partner, int):
                partner = partner.id
            if product:
                if not isinstance(product, int):
                    product = product.id
                customerinfo_id = self.customer_ids.filtered(
                    lambda x: x.name.id == partner and x.product_id.id == product
                )
            else:
                customerinfo_id = self.customer_ids.filtered(
                    lambda x: x.name.id == partner
                )
            return customerinfo_id[0].product_name if customerinfo_id else False
        return False

    def _get_combination_info(
        self,
        combination=False,
        product_id=False,
        add_qty=1,
        pricelist=False,
        parent_combination=False,
        only_template=False,
    ):
        new_self = self
        if (
            not self.env.context.get("partner")
            and not self.env.context.get("partner_id")
            and self.env.user.partner_id
        ):
            new_self = self.with_context(partner=self.env.user.partner_id.id)
        res = super(ProductTemplate, new_self)._get_combination_info(
            combination,
            product_id,
            add_qty,
            pricelist,
            parent_combination,
            only_template,
        )
        new_display_name = new_self._get_customerinfo_name(
            new_self.env.context.get("partner")
            or new_self.env.context.get("partner_id"),
            new_self.env.context.get("product_id"),
        )
        if new_display_name:
            res.update(display_name=new_display_name)
        return res

    def price_compute(self, price_type, uom=False, currency=False, company=None):
        if price_type == "partner" and self.product_variant_count == 1:
            price_type = "partner_price"
        elif price_type == "partner":
            price_type = "list_price"
        return super(ProductTemplate, self).price_compute(
            price_type, uom, currency, company
        )
