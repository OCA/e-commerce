# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import HttpCase


class UICase(HttpCase):
    def setUp(self):
        super().setUp()
        init_category = self.env["product.public.category"].create(
            {"name": "Init Category"}
        )
        self.env["product.template"].create(
            {
                "name": "Test Product 1",
                "is_published": True,
                "website_sequence": 1,
                "type": "consu",
                "public_categ_ids": [init_category.id],
            }
        )
        self.website = self.env["website"].browse(1)
        self.website.update({"init_category_id": init_category.id})
        self.env.ref("website_sale.products_categories").active = True

    def test_ui_website(self):
        """Test frontend tour."""
        tour = (
            "odoo.__DEBUG__.services['web_tour.tour']",
            "website_sale_init_category",
        )
        self.browser_js(
            url_path="/shop",
            code="%s.run('%s')" % tour,
            ready="%s.tours['%s'].ready" % tour,
            login="admin",
        )
