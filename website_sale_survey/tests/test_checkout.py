# Copyright 2021 Tecnativa - Jairo Llopis
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import Form, HttpCase


class UICase(HttpCase):
    def setUp(self):
        super().setUp()
        self.open_stage = self.env["survey.stage"].create({"name": "open"})
        self.survey = self.env["survey.survey"].create(
            {
                "title": "survey 1",
                "stage_id": self.open_stage.id,
                "page_ids": [
                    (
                        0,
                        0,
                        {
                            "title": "page 1",
                            "question_ids": [
                                (
                                    0,
                                    0,
                                    {
                                        "question": "are you a robot?",
                                        "type": "textbox",
                                    },
                                )
                            ],
                        },
                    )
                ],
            }
        )
        self.products = self.env["product.product"].create(
            [
                {
                    "list_price": 10,
                    "name": "website_sale_survey test product without surveys",
                    "website_published": True,
                },
                {
                    "list_price": 20,
                    "name": "website_sale_survey test product with surveys 1",
                    "survey_id": self.survey.id,
                    "website_published": True,
                },
                {
                    "list_price": 30,
                    "name": "website_sale_survey test product with surveys 2",
                    "survey_id": self.survey.id,
                    "website_published": True,
                },
            ]
        )

    def test_checkout(self):
        """Test checkout process completes as expected."""
        tour = "website_sale_survey_checkout"
        self.browser_js(
            url_path="/shop",
            code="odoo.__DEBUG__.services['web_tour.tour'].run('%s')" % tour,
            ready="odoo.__DEBUG__.services['web_tour.tour'].tours.%s.ready" % tour,
        )
        # Check that answers got linked to sale order lines
        for product, answer in zip(self.products, (False, "of course", "again?")):
            line = self.env["sale.order.line"].search([("product_id", "=", product.id)])
            self.assertEqual(
                line.survey_user_input_ids.user_input_line_ids.value_text, answer
            )
