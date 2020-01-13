# Copyright 2020 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade


_field_renames = [
    ('product.secondary.unit', 'product_secondary_unit',
     'website_published', 'is_published'),
]


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_fields(env, _field_renames)
