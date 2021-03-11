# Copyright 2021 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    """We avoid the error of selection option not valid changing to the current
    default one. On OpenUpgrade itself, the field website_description is
    swapped to change the content of the field to match the new criteria.
    """
    openupgrade.logged_query(
        env.cr,
        """UPDATE website
        SET default_product_sort_criteria = 'website_sequence asc'
        WHERE default_product_sort_criteria = 'website_sequence desc'""",
    )
