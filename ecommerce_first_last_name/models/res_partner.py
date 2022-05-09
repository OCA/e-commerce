from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    last_name = fields.Char()
