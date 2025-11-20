# Copyright 2025 Onestein (<https://www.onestein.nl>)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl)

from odoo import fields, models


class SendcloudSyncWizard(models.TransientModel):
    _inherit = "sendcloud.sync.wizard"

    publish_all_shipping_methods = fields.Boolean()

    def button_sync(self):
        ctx = self.env.context.copy()
        if self.publish_all_shipping_methods:
            ctx["sendcloud_publish_all_shipping_methods"] = True
        return super(SendcloudSyncWizard, self.with_context(**ctx)).button_sync()
