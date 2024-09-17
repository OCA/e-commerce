# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import HttpCase
from odoo.addons.base.tests.common import DISABLED_MAIL_CONTEXT


class UICase(HttpCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, **DISABLED_MAIL_CONTEXT))
        category_posted = cls.env["product.public.category"].create(
            {"name": "Category Test Posted"}
        )
        cls.env["product.public.category"].create({"name": "Category Test Not Posted"})
        cls.env["product.template"].create(
            {
                "name": "Test Product 1",
                "is_published": True,
                "website_sequence": 1,
                "type": "consu",
                "public_categ_ids": [category_posted.id],
            }
        )
        cls.env.ref("website_sale.products_categories").active = True

    def test_ui_website(self):
        """Test frontend tour."""
        tour = (
            "odoo.__DEBUG__.services['web_tour.tour']",
            "website_sale_hide_empty_category",
        )
        self.browser_js(
            url_path="/shop",
            code="%s.run('%s')" % tour,
            ready="%s.tours['%s'].ready" % tour,
            login="admin",
        )
