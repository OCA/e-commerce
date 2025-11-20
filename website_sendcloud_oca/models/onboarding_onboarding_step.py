# Copyright 2025 Onestein (<https://www.onestein.nl>)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl)

from odoo import api, models


class OnboardingStep(models.Model):
    _inherit = "onboarding.onboarding.step"

    @api.model
    def action_open_sendcloud_onboarding_website_brand(self):
        """Called by onboarding panel."""
        action_name = "website_sendcloud_oca.action_sendcloud_onboarding_website_wizard"
        return self.env.ref(action_name).read()[0]
