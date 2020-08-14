# Copyright 2020 Jairo Llopis - Tecnativa
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo.tests.common import HttpCase, Form


class UICase(HttpCase):
    def setUp(self):
        super().setUp()
        # Create and select a pricelist
        # to make tests pass no matter what l10n package is enabled
        website = self.env["website"].get_current_website()
        pricelist = self.env["product.pricelist"].create({
            "name": "website_sale_b2x_alt_price public",
            "currency_id": website.user_id.company_id.currency_id.id,
            "selectable": True,
        })
        website.user_id.property_product_pricelist = pricelist
        # Create some demo taxes
        self.tax_group_22 = self.env["account.tax.group"].create(
            {"name": "Tax group 22%"}
        )
        self.tax_22_sale = self.env["account.tax"].create(
            {
                "amount_type": "percent",
                "amount": 22,
                "description": "22%",
                "name": "Tax sale 22%",
                "tax_group_id": self.tax_group_22.id,
                "type_tax_use": "sale",
            }
        )
        self.tax_22_purchase = self.env["account.tax"].create(
            {
                "amount_type": "percent",
                "amount": 22,
                "description": "22%",
                "name": "Tax purchase 22%",
                "tax_group_id": self.tax_group_22.id,
                "type_tax_use": "purchase",
            }
        )
        # Create one product without taxes
        self.training_accounting = self.env["product.template"].create(
            {
                "name": "Training on accounting - website_sale_b2x_alt_price",
                "list_price": 100,
                "type": "service",
                "website_published": True,
                "uom_id": self.ref("uom.product_uom_unit"),
                "uom_po_id": self.ref("uom.product_uom_unit"),
                "taxes_id": [(5, 0, 0)],
                "supplier_taxes_id": [(5, 0, 0)],
            }
        )
        # One product with taxes
        self.pen = self.env["product.template"].create(
            {
                "name": "Pen - website_sale_b2x_alt_price",
                "list_price": 5,
                "type": "consu",
                "website_published": True,
                "uom_id": self.ref("uom.product_uom_unit"),
                "uom_po_id": self.ref("uom.product_uom_unit"),
                "description_sale": "Best. Pen. Ever.",
                "taxes_id": [(6, 0, [self.tax_22_sale.id])],
                "supplier_taxes_id": [(6, 0, [self.tax_22_purchase.id])],
            }
        )
        # One product with taxes and variants
        self.notebook = self.env["product.template"].create(
            {
                "name": "Notebook - website_sale_b2x_alt_price",
                "list_price": 3,
                "type": "consu",
                "website_published": True,
                "uom_id": self.ref("uom.product_uom_unit"),
                "uom_po_id": self.ref("uom.product_uom_unit"),
                "description_sale": "Best. Notebook. Ever.",
                "taxes_id": [(6, 0, [self.tax_22_sale.id])],
                "supplier_taxes_id": [(6, 0, [self.tax_22_purchase.id])],
            }
        )
        self.sheet_size = self.env["product.attribute"].create(
            {"name": "Sheet size", "type": "radio", "create_variant": "always"}
        )
        self.sheet_size_a4 = self.env["product.attribute.value"].create(
            {"name": "A4", "attribute_id": self.sheet_size.id, "sequence": 20}
        )
        self.sheet_size_a5 = self.env["product.attribute.value"].create(
            {"name": "A5", "attribute_id": self.sheet_size.id, "sequence": 10}
        )
        self.notebook_a4 = self.env["product.product"].create(
            {
                "default_code": "NB_A4",
                "product_tmpl_id": self.notebook.id,
                "attribute_value_ids": [(6, 0, self.sheet_size_a4.ids)],
            }
        )
        self.notebook_a5 = self.env["product.product"].create(
            {
                "default_code": "NB_A5",
                "product_tmpl_id": self.notebook.id,
                "attribute_value_ids": [(6, 0, self.sheet_size_a5.ids)],
            }
        )
        self.notebook_attline_sheet_size = self.env[
            "product.template.attribute.line"
        ].create(
            {
                "product_tmpl_id": self.notebook.id,
                "attribute_id": self.sheet_size.id,
                "value_ids":
                    [(6, 0, [self.sheet_size_a4.id, self.sheet_size_a5.id])],
            }
        )
        # A4 notebook is slightly more expensive
        self.notebook_a4.product_template_attribute_value_ids.price_extra = 0.5
        # Create a pricelist selectable from website with 10% discount
        self.discount_pricelist = self.env["product.pricelist"].create(
            {
                "name": "website_sale_b2x_alt_price discounted",
                "discount_policy": "without_discount",
                "selectable": True,
                "item_ids": [
                    (
                        0,
                        0,
                        {
                            "applied_on": "3_global",
                            "compute_price": "percentage",
                            "percent_price": 10,
                        },
                    ),
                ],
            }
        )

    def _switch_tax_mode(self, mode):
        assert mode in {"tax_excluded", "tax_included"}
        config = Form(self.env["res.config.settings"])
        config.show_line_subtotals_tax_selection = mode
        config.multi_sales_price = True
        config.multi_sales_price_method = "formula"
        config.group_discount_per_so_line = True
        config = config.save()
        config.execute()

    def test_ui_website_b2b(self):
        """Test frontend b2b tour."""
        self._switch_tax_mode("tax_excluded")
        # TODO Use self.start_tour in v13
        service = "odoo.__DEBUG__.services['web_tour.tour']"
        tour_name = "website_sale_b2x_alt_price_b2b"
        self.browser_js(
            url_path="/shop?search=website_sale_b2x_alt_price",
            code="{}.run('{}')".format(
                service,
                tour_name
            ),
            ready="{}.tours.{}.ready".format(
                service,
                tour_name
            ),
        )

    def test_ui_website_b2c(self):
        """Test frontend b2c tour."""
        self._switch_tax_mode("tax_included")
        # TODO Use self.start_tour in v13
        service = "odoo.__DEBUG__.services['web_tour.tour']"
        tour_name = "website_sale_b2x_alt_price_b2c"
        self.browser_js(
            url_path="/shop?search=website_sale_b2x_alt_price",
            code="{}.run('{}')".format(
                service,
                tour_name
            ),
            ready="{}.tours.{}.ready".format(
                service,
                tour_name
            ),
        )
