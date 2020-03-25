from odoo import fields, models


class res_company(models.Model):
    _inherit = 'res.company'
    
    must_validate_vat = fields.Boolean('Mandatory online verification?', help='If enabled, the system validates VAT number online and shows error message if given VAT number of partner/customer is not valid.')
