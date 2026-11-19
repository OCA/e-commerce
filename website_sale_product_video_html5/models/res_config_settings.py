# Copyright 2026 Bosd
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    product_video_allowed_hosts = fields.Char(
        string="Product Video Hosts",
        config_parameter="website_sale_product_video_html5.allowed_hosts",
        help="Comma-separated list of hosts serving product videos from URLs "
        "without a file extension, e.g. res.cloudinary.com. Subdomains are "
        "included.",
    )
