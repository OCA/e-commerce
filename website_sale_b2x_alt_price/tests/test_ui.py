# Copyright 2020 Jairo Llopis - Tecnativa
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo.tests import Form
from odoo.tests.common import HttpCase, tagged

from odoo.addons.base.tests.common import DISABLED_MAIL_CONTEXT


@tagged("post_install", "-at_install")
class UICase(HttpCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, **DISABLED_MAIL_CONTEXT))
        # Create and select a pricelist
        # to make tests pass no matter what l10n package is enabled
        website = cls.env["website"].get_current_website()
        pricelist = cls.env["product.pricelist"].create(
            {
                "name": "website_sale_b2x_alt_price public",
                "currency_id": website.user_id.company_id.currency_id.id,
                "selectable": True,
            }
        )
        website.user_id.property_product_pricelist = pricelist
        admin = cls.env.ref("base.user_admin")
        admin.property_product_pricelist = pricelist
        # Create some demo taxes
        cls.tax_group_22 = cls.env["account.tax.group"].create(
            {"name": "Tax group 22%"}
        )
        cls.tax_22_sale = cls.env["account.tax"].create(
            {
                "amount_type": "percent",
                "amount": 22,
                "description": "22%",
                "name": "Tax sale 22%",
                "tax_group_id": cls.tax_group_22.id,
                "type_tax_use": "sale",
            }
        )
        cls.tax_22_purchase = cls.env["account.tax"].create(
            {
                "amount_type": "percent",
                "amount": 22,
                "description": "22%",
                "name": "Tax purchase 22%",
                "tax_group_id": cls.tax_group_22.id,
                "type_tax_use": "purchase",
            }
        )
        # Create one product without taxes
        cls.training_accounting = cls.env["product.template"].create(
            {
                "name": "Training on accounting - website_sale_b2x_alt_price",
                "list_price": 100,
                "type": "service",
                "website_published": True,
                "uom_id": cls.env.ref("uom.product_uom_unit").id,
                "uom_po_id": cls.env.ref("uom.product_uom_unit").id,
                "taxes_id": [(5, 0, 0)],
                "supplier_taxes_id": [(5, 0, 0)],
            }
        )
        # One product with taxes
        cls.pen = cls.env["product.template"].create(
            {
                "name": "Pen - website_sale_b2x_alt_price",
                "list_price": 5,
                "type": "consu",
                "website_published": True,
                "uom_id": cls.env.ref("uom.product_uom_unit").id,
                "uom_po_id": cls.env.ref("uom.product_uom_unit").id,
                "description_sale": "Best. Pen. Ever.",
                "taxes_id": [(6, 0, [cls.tax_22_sale.id])],
                "supplier_taxes_id": [(6, 0, [cls.tax_22_purchase.id])],
            }
        )
        # One product with taxes and variants
        cls.notebook = cls.env["product.template"].create(
            {
                "name": "Notebook - website_sale_b2x_alt_price",
                "list_price": 3,
                "type": "consu",
                "website_published": True,
                "uom_id": cls.env.ref("uom.product_uom_unit").id,
                "uom_po_id": cls.env.ref("uom.product_uom_unit").id,
                "description_sale": "Best. Notebook. Ever.",
                "taxes_id": [(6, 0, [cls.tax_22_sale.id])],
                "supplier_taxes_id": [(6, 0, [cls.tax_22_purchase.id])],
            }
        )
        cls.sheet_size = cls.env["product.attribute"].create(
            {"name": "Sheet size", "create_variant": "always"}
        )
        cls.sheet_size_a4 = cls.env["product.attribute.value"].create(
            {"name": "A4", "attribute_id": cls.sheet_size.id, "sequence": 20}
        )
        cls.sheet_size_a5 = cls.env["product.attribute.value"].create(
            {"name": "A5", "attribute_id": cls.sheet_size.id, "sequence": 10}
        )
        cls.notebook_attline = cls.env["product.template.attribute.line"].create(
            {
                "product_tmpl_id": cls.notebook.id,
                "attribute_id": cls.sheet_size.id,
                "value_ids": [(6, 0, [cls.sheet_size_a4.id, cls.sheet_size_a5.id])],
            }
        )
        cls.notebook_size_a4 = cls.notebook_attline.product_template_value_ids[1]
        cls.notebook_size_a5 = cls.notebook_attline.product_template_value_ids[0]
        cls.notebook_a4 = cls.notebook._get_variant_for_combination(
            cls.notebook_size_a4
        )
        cls.notebook_a4.write(
            {"default_code": "NB_A4", "product_tmpl_id": cls.notebook.id}
        )
        cls.notebook_a5 = cls.notebook._get_variant_for_combination(
            cls.notebook_size_a5
        )
        cls.notebook_a5.write(
            {"default_code": "NB_A5", "product_tmpl_id": cls.notebook.id}
        )
        # A4 notebook is slightly more expensive
        cls.notebook_a4.product_template_attribute_value_ids.price_extra = 0.5
        # Create a pricelist selectable from website with 10% discount
        cls.discount_pricelist = cls.env["product.pricelist"].create(
            {
                "name": "website_sale_b2x_alt_price discounted",
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
        config.group_product_pricelist = True
        config.group_discount_per_so_line = True
        config = config.save()
        config.execute()

    def test_ui_website_b2b(self):
        """Test frontend b2b tour."""
        self._switch_tax_mode("tax_excluded")
        self.start_tour(
            "/shop?search=website_sale_b2x_alt_price",
            "website_sale_b2x_alt_price_b2b",
            login="admin",
        )

    def test_ui_website_b2c(self):
        """Test frontend b2c tour."""
        self._switch_tax_mode("tax_included")
        self.start_tour(
            "/shop?search=website_sale_b2x_alt_price",
            "website_sale_b2x_alt_price_b2c",
            login="admin",
        )
