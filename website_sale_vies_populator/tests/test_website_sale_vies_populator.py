# Copyright 2026 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)

import json
import unittest

from odoo.tests.common import HttpCase, tagged

from odoo.addons.partner_data_vies_populator.tests import (
    test_partner_data_vies_populator,
)


@tagged("-at_install", "post_install")
class TestWebsiteSaleViesPopulator(
    HttpCase, test_partner_data_vies_populator.TestPartnerCreateByVAT
):
    def test_get_vies_data(self):
        """Test vies endpoint"""
        result = self.url_open(
            "/website_sale_vies_populator/get_vies_data",
            data=json.dumps(
                {
                    "id": 0,
                    "jsonrpc": "2.0",
                    "method": "call",
                    "params": {
                        "vat": "BE0477472701",
                    },
                }
            ),
            headers={
                "Content-Type": "application/json",
            },
        ).json()
        self.assertEqual(result["result"]["vat"], "BE0477472701")

    # deactivate inherited tests, can be removed in > v18

    @unittest.skip("inherited")
    def test_create_from_vat1(self):
        pass

    @unittest.skip("inherited")
    def test_create_from_vat2nl(self):
        pass

    @unittest.skip("inherited")
    def test_company_vat_change(self):
        pass

    @unittest.skip("inherited")
    def test_empty_vat_change(self):
        pass

    @unittest.skip("inherited")
    def test_individual_vat_change(self):
        pass

    @unittest.skip("inherited")
    def test_non_eu_vat_change(self):
        pass

    @unittest.skip("inherited")
    def test_empty_fields(self):
        pass
