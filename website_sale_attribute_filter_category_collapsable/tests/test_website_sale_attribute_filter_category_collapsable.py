# Copyright 2020 Tecnativa - Alexandre D. Díaz
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.addons.website_sale_attribute_filter_category.tests.test_website_sale_attribute_filter_category import websiteSaleAttributeFilterCategoryHttpCase as TestCase  # noqa: E501


class websiteSaleAttributeFilterCategoryCollapsableHttpCase(TestCase):

    def test_ui_website(self):
        """Test frontend tour."""
        tour = (
            "odoo.__DEBUG__.services['web_tour.tour']",
            "website_sale_attribute_filter_category_collapsable",
        )
        self.browser_js(
            url_path="/",
            code="%s.run('%s')" % tour,
            ready="%s.tours['%s'].ready" % tour,
            login="admin"
        )
