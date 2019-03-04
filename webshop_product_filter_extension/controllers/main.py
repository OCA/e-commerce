# -*- coding: utf-8 -*-
import openerp.addons.website_sale.controllers.main as main


class WebsiteSale(main.website_sale):

    def get_category_attributes(self, category):
        result = super(WebsiteSale, self).get_category_attributes(category)
        return result.filtered('is_filter')
