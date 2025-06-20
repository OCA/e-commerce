# Copyright 2025 Tecnativa - Víctor Martínez
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from openupgradelib import openupgrade

_deleted_xml_records = ["website_sale_resource_booking.wizard_checkout"]


@openupgrade.migrate()
def migrate(env, version):
    env["ir.ui.view"].search(
        [
            ("key", "=", "website_sale_resource_booking.wizard_checkout"),
            ("website_id", "!=", False),
        ]
    ).unlink()
    openupgrade.delete_records_safely_by_xml_id(
        env,
        _deleted_xml_records,
    )
