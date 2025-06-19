# Copyright 2025 Tecnativa - Pilar Vargas
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE website
        SET show_line_subtotals_tax_selection =
            CASE
                WHEN tax_toggle_preactivated IS TRUE THEN 'tax_included'
                ELSE 'tax_excluded'
            END
        WHERE tax_toggle_preactivated IS NOT NULL;
        """,
    )
