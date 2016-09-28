# -*- coding: utf-8 -*-
# © 2016 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.addons.website_supplier_list.controllers.main \
    import WebsiteSupplier
from openerp.addons.website_sale.controllers.main import website_sale
from openerp.addons.web import http
from openerp.addons.web.http import request


class WebsiteSaleBySupplier(WebsiteSupplier):
    @http.route()
    def partners_detail(self, partner_id, **post):
        response = super(WebsiteSaleBySupplier, self).partners_detail(
            partner_id)
        product_ids = []
        partner = []
        obj_product_supplierinfo = request.env['product.supplierinfo']
        obj_partner = request.env['res.partner']
        if partner_id:
            partner = obj_partner.browse(partner_id)
            if partner.exists() and partner.website_supplier_published:
                domain = [
                    ('name', '=', partner_id)
                ]
                supplierinfo_ids = obj_product_supplierinfo.search(domain)

                for supplierinfo in supplierinfo_ids:
                    if supplierinfo.product_tmpl_id.website_published:
                        product_ids.append(supplierinfo.product_tmpl_id)

        response.qcontext['products'] = product_ids

        return response


class WebsiteSale(website_sale):
    @http.route(['/shop',
                 '/shop/page/<int:page>',
                 '/shop/category/<model("product.public.category"):category>',
                 """/shop/category/<model("product.public.category"):category>
                 /page/<int:page>""",
                 '/shop/suppliers/<model("res.partner"):product_supplier>'])
    def shop(
        self,
        page=0,
        category=None,
        product_supplier=None,
        search='',
        **post
    ):
        if product_supplier:
            request.context.setdefault('supplier_id', int(product_supplier))
        result = super(WebsiteSale, self).shop(
            page=page,
            category=category,
            search=search,
            **post)
        result.qcontext['product_supplier'] = product_supplier
        return result
