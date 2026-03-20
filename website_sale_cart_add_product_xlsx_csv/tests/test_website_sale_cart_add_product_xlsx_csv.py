# Copyright 2025 Alberto Martínez <alberto.martinez@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from io import BytesIO

from werkzeug.datastructures import FileStorage

from odoo.tests.common import tagged
from odoo.tools.misc import file_path

from odoo.addons.website.tools import MockRequest
from odoo.addons.website_sale.tests.test_website_sale_cart import WebsiteSaleCart
from odoo.addons.website_sale_cart_add_product_xlsx_csv.controllers.main import (
    WebsiteSaleAddProductXlsxCsv,
)


@tagged("post_install", "-at_install")
class TestWebsiteSaleCartAddProductXlsxCsv(WebsiteSaleCart):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.WebsiteSaleControllerAddProductXlsxCsv = WebsiteSaleAddProductXlsxCsv()
        cls.file_route_csv = file_path(
            "website_sale_cart_add_product_xlsx_csv/static/xlsx/import_unit_test.csv"
        )
        cls.file_route_xlsx = file_path(
            "website_sale_cart_add_product_xlsx_csv/static/xlsx/import_unit_test.xlsx"
        )
        cls.error_file_route_csv = file_path(
            "website_sale_cart_add_product_xlsx_csv/static/xlsx/import_unit_test.error"
        )

    def read_file(self, path):
        with open(path, "rb") as f:
            file = FileStorage(stream=BytesIO(f.read()), filename=path.split("/")[-1])
        return file

    def _test_import(self, file_route):
        website = self.website.with_user(self.public_user)
        with MockRequest(self.product.with_user(self.public_user).env, website=website):
            sale_order = website.sale_get_order(force_create=True)
            self.assertFalse(sale_order.order_line)
            self.WebsiteSaleControllerAddProductXlsxCsv.cart(
                cart_file=self.read_file(file_route)
            )
            self.assertTrue(sale_order.order_line)

    def test_import_csv(self):
        self._test_import(self.file_route_csv)

    def test_import_xlsx(self):
        self._test_import(self.file_route_xlsx)

    def test_import_vals(self):
        website = self.website.with_user(self.public_user)
        with MockRequest(self.product.with_user(self.public_user).env, website=website):
            sale_order = website.sale_get_order(force_create=True)
            self.assertFalse(sale_order.order_line)
            (
                import_status,
                _,
                failed_products,
            ) = self.WebsiteSaleControllerAddProductXlsxCsv.import_file(
                sale_order, self.read_file(self.file_route_csv)
            )
            self.assertEqual(import_status, "warn")
            product_to_fail = ["FURN_7800", "FURN_9001", "Inexistent"]
            failed_products = "\n".join(failed_products)
            for p in product_to_fail:
                self.assertIn(p, failed_products)

    def test_import_error(self):
        website = self.website.with_user(self.public_user)
        with MockRequest(self.product.with_user(self.public_user).env, website=website):
            sale_order = website.sale_get_order(force_create=True)
            self.assertFalse(sale_order.order_line)
            self.WebsiteSaleControllerAddProductXlsxCsv.cart(
                cart_file=self.read_file(self.error_file_route_csv)
            )
            self.assertFalse(sale_order.order_line)

    def test_import_error_vals(self):
        website = self.website.with_user(self.public_user)
        with MockRequest(self.product.with_user(self.public_user).env, website=website):
            sale_order = website.sale_get_order(force_create=True)
            self.assertFalse(sale_order.order_line)
            (
                import_status,
                _,
                _,
            ) = self.WebsiteSaleControllerAddProductXlsxCsv.import_file(
                sale_order, self.read_file(self.error_file_route_csv)
            )
            self.assertEqual(import_status, "error")
