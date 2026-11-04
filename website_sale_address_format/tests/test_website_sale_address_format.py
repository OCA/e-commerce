# Copyright 2020-2022 Quartile Limited
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests import common, tagged


@tagged("post_install", "-at_install")
class TestWebsiteSaleAddressFormat(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.japan = cls.env.ref("base.jp")

    def test_00_country_infos(self):
        self.japan.online_address_format = """
            %(zip)s
            %(state_name)s %(city)s
            %(street)s
            %(street2)s
        """
        vals1 = self.japan.get_online_address_fields()
        vals1_sorted = ["zip", "state_name", "city", "street", "street2"]
        self.assertEqual(vals1, vals1_sorted)
        self.japan.online_address_format = """
            %(state_name)s %(city)s
            %(zip)s
            %(street)s
            %(street2)s
            %(country_code)s
        """
        vals2 = self.japan.get_online_address_fields()
        vals2_sorted = [
            "state_name",
            "city",
            "zip",
            "street",
            "street2",
            "country_code",
        ]
        self.assertEqual(vals2, vals2_sorted)
