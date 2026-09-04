# Copyright 2026 ForgeFlow S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import base64

from odoo import http
from odoo.http import request


class ProductInquiryController(http.Controller):
    @http.route(
        "/shop/product/inquiry",
        type="http",
        auth="public",
        methods=["POST"],
        website=True,
        csrf=False,
    )
    def product_inquiry(self, **kwargs):
        product_id = kwargs.get("product_id", "").strip()
        contact_name = kwargs.get("contact_name", "").strip()
        email = kwargs.get("email", "").strip()
        phone = kwargs.get("phone", "").strip()
        company_name = kwargs.get("company_name", "").strip()
        inquiry_type = kwargs.get("inquiry_type", "more_info")
        question = kwargs.get("question", "").strip()

        if not product_id or not contact_name or not email or not question:
            return request.make_json_response(
                {"success": False, "error": "Required fields are missing."},
                status=400,
            )
        try:
            product_id = int(product_id)
        except (ValueError, TypeError):
            return request.make_json_response(
                {"success": False, "error": "Invalid product."}, status=400
            )
        variant = request.env["product.product"].sudo().browse(product_id)
        if not variant.exists():
            return request.make_json_response(
                {"success": False, "error": "Product not found."}, status=404
            )
        description = f"<p>{question}</p>"
        lead_vals = {
            "name": f"Product inquiry: {variant.product_tmpl_id.name}",
            "contact_name": contact_name,
            "email_from": email,
            "phone": phone or False,
            "partner_name": company_name or False,
            "inquired_product_id": variant.id,
            "inquiry_type": inquiry_type,
            "description": description,
            "type": "lead",
            "company_id": request.website.company_id.id,
        }
        salesperson_id = self._get_product_salesperson(variant)  # pylint: disable=assignment-from-none
        if salesperson_id is not None:
            lead_vals["user_id"] = salesperson_id or False
        lead = request.env["crm.lead"].sudo().create(lead_vals)
        attachment_file = kwargs.get("attachment")
        if attachment_file and hasattr(attachment_file, "read"):
            data = attachment_file.read()
            if data:
                request.env["ir.attachment"].sudo().create(
                    {
                        "name": attachment_file.filename,
                        "datas": base64.b64encode(data),
                        "res_model": "crm.lead",
                        "res_id": lead.id,
                    }
                )
        return request.make_json_response({"success": True})

    def _get_product_salesperson(self, variant):
        """Return salesperson assignment for the lead.
        - Return a user ID to assign that user.
        - Return False to explicitly leave user_id blank.
        - Return None (default) to let the model default apply.
        """
        return None
