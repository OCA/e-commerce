# Copyright 2026 ADHOC SA
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import logging

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)

MODULE = "website_sale_product_attribute_value_filter_existing"
VIEWS = (
    "filter_select_attributes",
    "filter_radio_and_multi_attributes",
    "filter_pills_attributes",
    "filter_color_attributes",
    "filter_image_attributes",
)
OLD_ANCHOR = "[@t-foreach='a.value_ids']"
NEW_ANCHOR = "[@t-foreach='pavs_per_attribute[a]']"
OLD_SYMBOL = "a.value_ids"


def migrate(cr, version):
    """Retarget the anchor kept by the website-specific copies of our views.

    The update propagates our new arch to the copy-on-write copies whose own
    arch still matches the generic one (`ir.ui.view._load_records_write`), but
    not to the ones that were edited: those keep the 19.0 anchor, which no
    longer locates, and the shop page then fails to render for that website.
    """
    keys = tuple(f"{MODULE}.{view}" for view in VIEWS)
    # `arch_db` is a translated jsonb column: patch every language at once.
    cr.execute(
        """
        UPDATE ir_ui_view
           SET arch_db = replace(arch_db::text, %s, %s)::jsonb
         WHERE website_id IS NOT NULL
           AND key IN %s
           AND strpos(arch_db::text, %s) > 0
        """,
        (OLD_ANCHOR, NEW_ANCHOR, keys, OLD_ANCHOR),
    )
    _logger.info("%s: retargeted %s website-specific views", MODULE, cr.rowcount)
    # Look for the symbol, not for the anchor just rewritten: a copy spelling it
    # otherwise (hand-edited quoting or spacing) is the one the replace above
    # cannot reach, and that website's shop page stays broken.
    cr.execute(
        "SELECT id FROM ir_ui_view WHERE website_id IS NOT NULL AND key IN %s"
        " AND strpos(arch_db::text, %s) > 0",
        (keys, OLD_SYMBOL),
    )
    if left := [row[0] for row in cr.fetchall()]:
        _logger.warning(
            "%s: these website-specific views still refer to `%s` and need a"
            " manual fix, their shop page will not render: %s",
            MODULE,
            OLD_SYMBOL,
            left,
        )
    # Writing the arch in SQL leaves the compiled templates behind.
    env = api.Environment(cr, SUPERUSER_ID, {})
    env.invalidate_all()
    env.transaction.invalidate_ormcache("templates")
