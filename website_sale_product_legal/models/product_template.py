# -*- coding: utf-8 -*-
# © 2015 Antiun Ingeniería, S.L. - Jairo Llopis
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    legal_term_ids = fields.Many2many(
        "website_sale_product_legal.legal_term",
        "website_sale_product_legal_rel",
        string="Legal terms",
        help="Online customers will be informed of these legal terms before "
             "buying this product.")
