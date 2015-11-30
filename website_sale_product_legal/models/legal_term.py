# -*- coding: utf-8 -*-
# © 2015 Antiun Ingeniería, S.L. - Jairo Llopis
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models


class LegalTerm(models.Model):
    _name = "website_sale_product_legal.legal_term"

    name = fields.Char(required=True, translate=True, index=True)
    contents = fields.Html(translate=True)
    product_template_ids = fields.Many2many(
        "product.template",
        "website_sale_product_legal_rel",
        string="Products",
        help="Products that require accepting this legal term.")
