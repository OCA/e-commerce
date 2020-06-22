# Copyright 2020 Tecnativa - Jairo Llopis
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo.http import request, route
from odoo.addons.website_sale.controllers import main


class WebsiteSale(main.WebsiteSale):
    @route()
    def product(self, *args, **kwargs):
        """Add filtered product downloads to render context."""
        result = super().product(*args, **kwargs)
        # Doing product.website_attachment_ids does not respect the domain
        # defined in the model; here we enforce that domain to make sure
        # we only render current website's attachments, and that there's no
        # difference between what the user sees in backend and what the visitor
        # sees in the frontend
        attachments_domain = request.env["product.template"].fields_get(
            ["website_attachment_ids"], ["domain"]
        )["website_attachment_ids"]["domain"]
        attachments = request.env["ir.attachment"].search(
            [("id", "in", result.qcontext["product"].website_attachment_ids.ids)]
            + attachments_domain,
            order="name"
        )
        result.qcontext["product_attachments"] = attachments
        return result
