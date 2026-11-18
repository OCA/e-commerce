# Copyright 2026 Sébastien Berger (sbinfo67)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0).

from odoo.addons.base.models.ir_model import MODULE_UNINSTALL_FLAG
from odoo.addons.payment import reset_payment_provider, setup_provider


def post_init_hook(env):
    setup_provider(env, "payplug")


def uninstall_hook(env):
    """Reset the Payplug providers, like the providers of the standard modules.

    Unlike them, the provider record belongs to this module and would be deleted with
    its data. Providers without transactions are deleted now; the others are kept
    (with the `none` code) and detached from this module so that their transactions
    stay readable.
    """
    providers = (
        env["payment.provider"]
        .with_context(active_test=False)
        .search([("code", "=", "payplug")])
    )
    used_providers = (
        env["payment.transaction"]
        .sudo()
        .search([("provider_id", "in", providers.ids)])
        .provider_id
    )
    reset_payment_provider(env, "payplug")
    env["ir.model.data"].search(
        [
            ("module", "=", "payment_payplug"),
            ("model", "=", "payment.provider"),
            ("res_id", "in", used_providers.ids),
        ]
    ).unlink()
    (providers - used_providers).with_context(**{MODULE_UNINSTALL_FLAG: True}).unlink()
