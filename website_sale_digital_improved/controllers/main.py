# Copyright 2026 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)

import time

from odoo import http

from odoo.addons.sale.controllers import portal


class CustomerPortal(portal.CustomerPortal):
    @http.route()
    def portal_order_page(self, *args, **post):
        # add timestamp+checksum to links to accessible digital products if not authenticated
        result = super().portal_order_page(*args, **post)
        if (
            result.qcontext.get("digital_attachments")
            and http.request.env["website"].is_public_user()
        ):
            Attachment = http.request.env["ir.attachment"].sudo()
            timestamp = int(time.time()) + int(
                http.request.env["ir.config_parameter"]
                .sudo()
                .get_param("website_sale_digital_improved.url_timeout")
                or 3600
            )
            for attachments in result.qcontext["digital_attachments"].values():
                for attachment_vals in attachments:
                    checksum = Attachment.browse(
                        attachment_vals["id"]
                    )._generate_download_checksum(timestamp)
                    attachment_vals["website_sale_digital_improved_url"] = (
                        f"/my/download?attachment_id={attachment_vals['id']}"
                        f"&timestamp={timestamp}&checksum={checksum}"
                    )
        return result

    @http.route()
    def download_attachment(self, attachment_id, timestamp=None, checksum=None):
        # sudo super if attachment is authenticated by checksum
        if timestamp and checksum and int(timestamp) > time.time():
            attachment = (
                http.request.env["ir.attachment"].sudo().browse(int(attachment_id))
            )
            if attachment._generate_download_checksum(timestamp) == checksum:
                http.request.update_env(su=True)
        return super().download_attachment(attachment_id)
