# -*- coding: utf-8 -*-
# © 2016 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import base64
import werkzeug
from openerp import http
import openerp.addons.website_sale.controllers.main as main


class WebsiteSale(main.website_sale):

    @http.route('/attachments/attachment/<model("ir.attachment")'
                ':attachment>', type='http', auth="public", website=True)
    def download_attachment(self, attachment):
        if attachment.public and attachment.res_model == 'product.template':
            filecontent = base64.b64decode(attachment.datas)
            disposition = 'attachment; filename=%s' % werkzeug.urls.url_quote(
                attachment.name)
            return http.request.make_response(
                filecontent,
                [('Content-Type', attachment.mimetype),
                 ('Content-Length', len(filecontent)),
                 ('Content-Disposition', disposition)])
        return http.request.website.render("website.403")
