from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    provisioning_time_in_workdays = fields.Integer(
        string="Provisioning time in workdays"
    )
