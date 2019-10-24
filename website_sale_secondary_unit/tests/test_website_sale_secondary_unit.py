# Copyright 2019 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.tests.common import HttpCase


class WebsiteSaleSecondaryUnitHttpCase(HttpCase):
    def setUp(self):
        super().setUp()
        # Models
        ProductSecondaryUnit = self.env['product.secondary.unit']
        product_uom_unit = self.env.ref('uom.product_uom_unit')
        self.product_template = self.env.ref(
            'product.product_product_4_product_template')
        vals = {
            'name': 'Box',
            'uom_id': product_uom_unit.id,
            'factor': 5.0,
            'product_tmpl_id': self.product_template.id,
            'website_published': True,
        }
        self.secondary_unit_box_5 = ProductSecondaryUnit.create(vals)
        self.secondary_unit_box_10 = ProductSecondaryUnit.create(
            dict(vals, factor=10.0))
        self.product_template.write({
            'secondary_uom_ids': [
                (6, 0, [self.secondary_unit_box_5.id,
                        self.secondary_unit_box_10.id]),
            ],
            'optional_product_ids': [(6, 0, [])]
        })

    def test_ui_website(self):
        """Test frontend tour."""
        tour = (
            "odoo.__DEBUG__.services['web_tour.tour']",
            "website_sale_secondary_unit",
        )
        self.browser_js(
            url_path="/",
            code="%s.run('%s')" % tour,
            ready="%s.tours['%s'].ready" % tour,
            login="admin")
