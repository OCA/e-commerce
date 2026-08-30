# Copyright 2026 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)

import time

from lxml import etree

from odoo import fields
from odoo.tests import tagged
from odoo.tests.common import HttpCase
from odoo.tools import mute_logger

from odoo.addons.account_payment.tests.common import AccountPaymentCommon
from odoo.addons.sale.tests.common import SaleCommon


@tagged("-at_install", "post_install")
class TestWebsiteSaleDigitalImproved(HttpCase, AccountPaymentCommon, SaleCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.sale_order = cls.env["sale.order"].create(
            {
                "partner_id": cls.env["res.partner"]
                .create(
                    {
                        "name": "testcustomer",
                        "email": "test@test.com",
                    }
                )
                .id,
                "order_line": [
                    fields.Command.create(
                        {
                            "product_id": cls.env.ref(
                                "website_sale_digital.product_1"
                            ).product_variant_ids.id,
                        }
                    ),
                ],
            }
        )
        cls.env["ir.config_parameter"].set_param("sale.automatic_invoice", "True")
        cls.attachment = cls.env.ref("website_sale_digital.attach1")

    def _pay_order(self):
        self.amount = self.sale_order.amount_total
        tx = self._create_transaction(
            flow="redirect", sale_order_ids=self.sale_order.ids, state="done"
        )
        with mute_logger("odoo.addons.sale.models.payment_transaction"):
            tx._reconcile_after_done()
        return self.sale_order.invoice_ids

    def test_mail(self):
        """
        Test that product is attached to invoice mail
        """
        invoices = self._pay_order()
        self.assertIn(
            self.attachment,
            invoices.message_ids.attachment_ids,
            "Invoice mail should have product attachment",
        )
        self.assertNotEqual(self.attachment, invoices.message_main_attachment_id)

    def test_access(self):
        result = self.url_open(
            f"/my/download?attachment_id={self.attachment.id}", allow_redirects=False
        )

        self.assertTrue(
            result.is_redirect and result.headers["Location"].endswith("/my/orders"),
            "Unauthenticated user should not be able to download product attachment "
            "without checksum",
        )

        now = int(time.time())

        attachment = self.url_open(
            f"/my/download?attachment_id={self.attachment.id}&"
            f"checksum={self.attachment._generate_download_checksum(now + 60)}&"
            f"timestamp={now + 60}"
        )

        self.assertEqual(attachment.content, self.attachment.raw)

        result = self.url_open(
            f"/my/download?attachment_id={self.attachment.id}&"
            f"checksum={self.attachment._generate_download_checksum(now)}&"
            f"timestamp={now}",
            allow_redirects=False,
        )

        self.assertTrue(
            result.is_redirect and result.headers["Location"].endswith("/my/orders"),
            "Expired timestamp should not allow access to attachment",
        )

        result = self.url_open(
            f"/my/download?attachment_id={self.attachment.id}&"
            "checksum=tampered_checksum&"
            f"timestamp={now + 60}",
            allow_redirects=False,
        )

        self.assertTrue(
            result.is_redirect and result.headers["Location"].endswith("/my/orders"),
            "Invalid checksum should not allow access to attachment",
        )

        order_token = self.sale_order._portal_ensure_token()

        portal_html = self.url_open(
            f"/my/orders/{self.sale_order.id}?access_token={order_token}"
        )
        self.assertNotIn(
            f"/my/download?attachment_id={self.attachment.id}",
            portal_html.content.decode("utf8"),
            "Download should not be offered for unpaid order",
        )

        self._pay_order()

        portal_html = self.url_open(
            f"/my/orders/{self.sale_order.id}?access_token={order_token}"
        )
        portal_html_doc = etree.fromstring(
            portal_html.content, parser=etree.HTMLParser()
        )
        download_link = portal_html_doc.xpath("//a[starts-with(@href, '/my/download')]")

        self.assertTrue(
            download_link, "Paid order accessed anonymously should have download link"
        )

        download_url = download_link[0].attrib["href"]
        attachment = self.url_open(download_url)
        self.assertEqual(attachment.content, self.attachment.raw)

        self.authenticate("admin", "admin")
        portal_html = self.url_open(
            f"/my/orders/{self.sale_order.id}?access_token={order_token}"
        )
        portal_html_doc = etree.fromstring(
            portal_html.content, parser=etree.HTMLParser()
        )
        download_link = portal_html_doc.xpath("//a[starts-with(@href, '/my/download')]")

        self.assertTrue(
            download_link, "Paid order accessed as admin should have download link"
        )

        self.assertNotIn(
            "checksum",
            download_link[0].attrib["href"],
            "Download link accessed with login should not have checksum",
        )
