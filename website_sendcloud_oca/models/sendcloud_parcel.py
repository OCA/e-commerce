# Copyright 2025 Onestein (<https://www.onestein.nl>)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl)

from odoo import api, models


class SendcloudParcel(models.Model):
    _inherit = "sendcloud.parcel"

    @api.depends("company_id")
    def _compute_brand_id(self):
        res = super()._compute_brand_id()
        for parcel in self:
            brand = parcel.picking_id.sale_id.website_id.sendcloud_brand_id
            if brand:
                parcel.brand_id = brand
        return res
