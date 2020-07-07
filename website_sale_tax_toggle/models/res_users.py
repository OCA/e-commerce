# Copyright 2020 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, models
from odoo.http import request
from odoo.tools import ormcache


class ResUsers(models.Model):
    _inherit = "res.users"

    @api.model
    def has_group(self, group_ext_id):
        tax_included = 'account.group_show_line_subtotals_tax_included'
        tax_excluded = 'account.group_show_line_subtotals_tax_excluded'
        if (self.env.context.get('website_id') and
                group_ext_id in [tax_included, tax_excluded] and
                not self.env.context.get('skip_tax_toggle_check')):
            taxed = request.session.get(
                'tax_toggle_taxed',
                self.env.user.with_context(
                    skip_tax_toggle_check=True
                ).has_group(tax_included)
            )
            return group_ext_id != (tax_excluded if taxed else tax_included)
        return super().has_group(group_ext_id)

    # HACK: To clear cache called from res.users write method
    @api.model
    @ormcache('self._uid', 'group_ext_id')
    def _has_group(self, group_ext_id):
        return super()._has_group(group_ext_id)

    has_group.clear_cache = _has_group.clear_cache
