# Copyright 2026 Sébastien Berger (sbinfo67)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0).

from odoo.tests import tagged

from ..hooks import uninstall_hook
from .common import PayplugCommon


@tagged("post_install", "-at_install", "payment_payplug")
class TestPayplugUninstallHook(PayplugCommon):
    def test_uninstall_hook(self):
        unused_provider = self.payplug.copy(
            {"name": "Payplug (unused)", "state": "disabled"}
        )
        tx = self._create_transaction("redirect")
        self.assertTrue(self.payplug.get_external_id()[self.payplug.id])

        uninstall_hook(self.env)

        # The provider without transactions is deleted with the module.
        self.assertFalse(unused_provider.exists())
        # The provider with transactions is reset and kept, detached from the module,
        # so that its transactions stay readable.
        self.assertTrue(self.payplug.exists())
        self.assertEqual(self.payplug.code, "none")
        self.assertEqual(self.payplug.state, "disabled")
        self.assertFalse(self.payplug.is_published)
        self.assertFalse(self.payplug.get_external_id()[self.payplug.id])
        self.assertEqual(tx.provider_id, self.payplug)
        self.assertFalse(
            self.env["payment.provider"]
            .with_context(active_test=False)
            .search([("code", "=", "payplug")])
        )
