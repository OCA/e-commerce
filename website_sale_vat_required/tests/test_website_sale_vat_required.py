# Copyright 2019 Tecnativa - Ernesto Tejeda
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.tests.common import HttpCase


class TestWebsiteSaleVatRequired(HttpCase):
    def test_website_sale_vat_required(self):
        if self.env["ir.module.module"]._get("payment_custom").state != "installed":
            self.skipTest("Transfer provider is not installed")

        transfer_provider = self.env.ref("payment.payment_provider_transfer")
        transfer_provider.write({"state": "enabled", "is_published": True})
        transfer_provider._transfer_ensure_pending_msg_is_set()

        self.env.user.partner_id.vat = False
        self.browser_js(
            url_path="/",
            code="odoo.__DEBUG__.services['web_tour.tour'].run('shop_buy_product')",
            ready="odoo.__DEBUG__.services['web_tour.tour']"
            ".tours.shop_buy_product.ready",
            login="admin",
        )
