# Copyright 2022-2022 Quartile Limited
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import re

from odoo import fields, models


class ResCountry(models.Model):
    _inherit = "res.country"

    online_address_format = fields.Text(
        string="Layout in eCommerce Address Forms",
        help="Display format to use for addresses belonging to this country in "
        "eCommerce address forms.\n\n"
        "You can use python-style string pattern with all the fields of the address "
        "(for example, use '%(street)s' to display the field 'street') plus"
        "\n%(state_name)s: the name of the state"
        "\n%(state_code)s: the code of the state"
        "\n%(country_name)s: the name of the country"
        "\n%(country_code)s: the code of the country",
    )

    def get_online_address_fields(self):
        self.ensure_one()
        return re.findall(r"\((.+?)\)", self.online_address_format)
