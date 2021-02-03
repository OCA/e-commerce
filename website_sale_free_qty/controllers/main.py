# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.http import request, route

from odoo.addons.website_sale_stock.controllers.main import WebsiteSale


class WebsiteSale(WebsiteSale):
    @route()
    def payment_transaction(self, *args, **kwargs):
        request.website = request.website.with_context(website_sale_free_qty=True)
        return super().payment_transaction(*args, **kwargs)
