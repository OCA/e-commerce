# Copyright 2026 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).


def post_init_hook(env):
    """Flip existing partners to the new default."""
    env["res.partner"].search([("skip_website_checkout_payment", "=", False)]).write(
        {"skip_website_checkout_payment": True}
    )
