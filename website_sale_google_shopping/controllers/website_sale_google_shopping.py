# -*- coding: utf-8 -*-
# License, author and contributors information in:
# __openerp__.py file at the root folder of this module.
from datetime import datetime, timedelta
import openerp
from functools import partial
from openerp import http
from openerp.http import request
from openerp.addons.website_sale.controllers.main import get_pricelist


DATE_FORMAT = '%Y-%m-%d %H:%M'
FEED_MIMETYPE = 'application/xml; charset=utf-8'


class GoogleShopping(http.Controller):
    def get_effective_date(self, date_start, date_end):
        if not date_start or not date_end:
            return ''
        ds = datetime.strptime(date_start, '%Y-%m-%d %H:%M:%S')
        de = datetime.strptime(date_end, '%Y-%m-%d %H:%M:%S')
        return '%sT%s/%sT%s' % (
            ds.strftime('%Y-%m-%d'),
            ds.strftime('%H:%M'),
            de.strftime('%Y-%m-%d'),
            de.strftime('%H:%M'))

    def generate_feed(self):
        env = request.env
        context = request.context
        url = '/google-shopping.xml'
        content = None
        ir_attachment = env['ir.attachment']
        attachments = ir_attachment.sudo().search_read([
            ('name', '=', url),
            ('type', '=', 'binary')],
            ('datas', 'create_date'))
        create_date = datetime.now()
        if attachments:
            server_format = openerp.tools.misc.DEFAULT_SERVER_DATETIME_FORMAT
            create_date = datetime.strptime(
                attachments[0]['create_date'], server_format)
            delta = datetime.now() - create_date
            if delta < timedelta(
                    hours=request.website.google_feed_expiry_time):
                content = attachments[0]['datas'].decode('base64')
        if not content:
            attachments = ir_attachment.search([
                ('name', '=', url),
                ('type', '=', 'binary')])
            if attachments:
                attachments.sudo().unlink()
            xml_id = 'website_sale_google_shopping.rss'

            context_copy = context.copy()
            if not context_copy.get('pricelist'):
                pricelist = get_pricelist()
                context_copy['pricelist'] = int(pricelist)
            else:
                pricelist = env['product.pricelist'].browse(
                    context_copy['pricelist'])
            products = env['product.template'].with_context(
                context_copy).sudo().search([
                    ('sale_ok', '=', True),
                    ('website_published', '=', True)])
            content = env.ref(xml_id).render(
                dict(
                    products=products,
                    url_root=request.httprequest.url_root[:-1],
                    updated=create_date.strftime('%Y-%m-%dT%H:%M:%SZ'),
                    get_effective_date=partial(self.get_effective_date)))
            # Replace to prevent error
            # XMLSyntaxError: Namespace prefix g on 'tag' is not defined
            content = content.replace('__colon__', ':')
            ir_attachment.sudo().create(dict(
                datas=content.encode('base64'),
                mimetype=FEED_MIMETYPE,
                type='binary',
                name=url,
                url=url,
            ))
        return content

    @http.route('/google-shopping.xml',
                type='http', auth='public', website=True)
    def feed_rss(self, **post):
        content = self.generate_feed()
        return request.make_response(content, headers=[
            ('Content-Type', FEED_MIMETYPE)])
