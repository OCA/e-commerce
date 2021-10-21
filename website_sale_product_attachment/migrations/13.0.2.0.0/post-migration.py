# Copyright 2021 Tecnativa - Pedro M. Baeza
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
from psycopg2 import sql

from odoo import tools


def migrate(cr, version):
    """Recover name column from v12 if exists to be used as website name."""
    column = "openupgrade_legacy_13_0_name"
    if tools.column_exists(cr, "ir_attachment", column):
        cr.execute(
            sql.SQL("UPDATE ir_attachment SET website_name = {}").format(
                sql.Identifier(column)
            )
        )
