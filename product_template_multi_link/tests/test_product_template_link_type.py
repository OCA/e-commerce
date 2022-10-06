# Copyright 2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from psycopg2 import IntegrityError

from odoo.tests import TransactionCase
from odoo.tools import mute_logger


class TestProductTemplateLinkType(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.LinkType = cls.env["product.template.link.type"]
        cls.link_type_cross_selling = cls.env.ref(
            "product_template_multi_link.product_template_link_type_cross_selling"
        )
        cls.link_type_range = cls.env.ref(
            "product_template_multi_link.product_template_link_type_demo_range"
        )
        cls.symmetric_link_without_code = cls.LinkType.create(
            {"name": "symmetric_link_without_code"}
        )
        cls.symmetric_link_with_code = cls.LinkType.create(
            {
                "name": "symmetric_link_with_code-name",
                "code": "symmetric_link_with_code-code",
            }
        )
        cls.asymmetric_link_without_inverse_code = cls.LinkType.create(
            {
                "is_symmetric": False,
                "name": "asymmetric_link_without_code-name",
                "inverse_name": "asymmetric_link_without_code-inverse_name",
            }
        )

        cls.asymmetric_link_with_inverse_code = cls.LinkType.create(
            {
                "is_symmetric": False,
                "name": "asymmetric_link_with_code-name",
                "inverse_name": "asymmetric_link_with_code-inverse_name",
                "inverse_code": "asymmetric_link_with_code-inverse_code",
            }
        )

    def test_0(self):
        """
        Data:
            None
        Test case:
            Create a link type by providing only the name
        Expected Result:
            by default link is symmetric
            inverse_name is computed
            inverse_name is equal to name
            code is false (not provided)
            inverse_code is false
        """
        link_type = self.LinkType.create({"name": "my type"})
        self.assertTrue(link_type.is_symmetric)
        self.assertTrue(link_type.name)
        self.assertEqual(link_type.name, link_type.inverse_name)
        self.assertFalse(link_type.code)
        self.assertFalse(link_type.inverse_code)

    def test_1(self):
        """
        Data:
            None
        Test case:
            Create a link type by providing only the name and the code
        Expected Result:
            by default link is symmetric
            inverse_name is computed
            inverse_name is equal to name
            inverse_code is computed
            inverse_code is equal to code
        """
        link_type = self.LinkType.create({"name": "my type", "code": "my-code"})
        self.assertTrue(link_type.is_symmetric)
        self.assertEqual(link_type.name, "my type")
        self.assertEqual(link_type.code, "my-code")
        self.assertEqual(link_type.name, link_type.inverse_name)
        self.assertEqual(link_type.code, link_type.inverse_code)

    @mute_logger("odoo.sql_db")
    def test_2(self):
        """
        Data:
            None
        Test case:
            Create a link type without providing the name
        Expected Result:
            Exception is raised
        """
        with self.assertRaises(IntegrityError), self.env.cr.savepoint():
            self.LinkType.create(
                {
                    "inverse_name": "my type",
                    "is_symmetric": False,
                    "code": "my_code",
                    "inverse_code": "my_inverse_code",
                }
            )

    def test_3(self):
        """
        Data:
            An existing symmetric link type
        Test case:
            Update the name
        Expected Result:
            inverse_name is still equal to name
        """
        self.assertEqual(
            self.link_type_cross_selling.name, self.link_type_cross_selling.inverse_name
        )
        self.link_type_cross_selling.write({"name": "new name"})
        self.assertEqual(self.link_type_cross_selling.name, "new name")
        self.assertEqual(
            self.link_type_cross_selling.name, self.link_type_cross_selling.inverse_name
        )

    def test_4(self):
        """
        Data:
            An existing symmetric link type
        Test case:
            Update the code
        Expected Result:
            inverse_code is still equal to code
        """
        self.assertEqual(
            self.link_type_cross_selling.code, self.link_type_cross_selling.inverse_code
        )
        self.link_type_cross_selling.write({"code": "new-code"})
        self.assertEqual(self.link_type_cross_selling.code, "new-code")
        self.assertEqual(
            self.link_type_cross_selling.code, self.link_type_cross_selling.inverse_code
        )

    def test_5(self):
        """
        Data:
            An existing symmetric link type
        Test case:
            Update the inverse_name
            Update the inverse_code
        Expected Result:
            inverse_name and inverse_code are not updated
        """
        self.assertEqual(
            self.link_type_cross_selling.name, self.link_type_cross_selling.inverse_name
        )
        self.assertEqual(
            self.link_type_cross_selling.code, self.link_type_cross_selling.inverse_code
        )
        inverse_name = self.link_type_cross_selling.inverse_name
        inverse_code = self.link_type_cross_selling.inverse_code
        self.link_type_cross_selling.write(
            {
                "inverse_name": "new " + inverse_name,
                "inverse_code": "new " + inverse_code,
            }
        )
        self.assertEqual(self.link_type_cross_selling.inverse_name, inverse_name)
        self.assertEqual(self.link_type_cross_selling.inverse_code, inverse_code)

    def test_6(self):
        """
        Data:
            An existing symmetric link type
        Test case:
            Update the inverse_name with name != inverse_name,
            code != inverse_code and make it asymmetric
        Expected Result:
            inverse_name is no more equal to name and
            the code is not more equald to inverse_code
        """
        self.assertEqual(
            self.link_type_cross_selling.name, self.link_type_cross_selling.inverse_name
        )
        self.assertEqual(
            self.link_type_cross_selling.code, self.link_type_cross_selling.inverse_code
        )
        self.link_type_cross_selling.write(
            {
                "is_symmetric": False,
                "inverse_name": "new inverse name",
                "inverse_code": "new inverse code",
            }
        )
        self.assertEqual(self.link_type_cross_selling.inverse_name, "new inverse name")
        self.assertEqual(self.link_type_cross_selling.inverse_code, "new inverse code")

    def test_7(self):
        """
        Data:
            An existing asymmetric link with inverse_code != code
            and inverse_name != name
        Test case:
            1 Make it symmetric
        Expected Result:
            invsere_code=code and inverse_name=name
        """
        self.assertFalse(self.link_type_range.is_symmetric)
        self.assertNotEqual(
            self.link_type_range.name, self.link_type_range.inverse_name
        )
        self.assertNotEqual(
            self.link_type_range.code, self.link_type_range.inverse_code
        )
        self.link_type_range.write({"is_symmetric": True})
        self.assertEqual(self.link_type_range.name, self.link_type_range.inverse_name)
        self.assertEqual(self.link_type_range.code, self.link_type_range.inverse_code)

    @mute_logger("odoo.sql_db")
    def test_8(self):
        """
        Data:
            symmetric link type without code
            symmetric link with code
            asymmetric link type without inverse_code
            asymmetric link type with inverse_code

        Test case:
            1 create a new link type with the same name without code
            1 create a new link type with the same name
            1 create a new link type with the same code
            1 create a new link type with the same inverse_name
        Expected Result:
            Intergrity Error
        """
        with self.assertRaises(IntegrityError), self.env.cr.savepoint():
            self.LinkType.create({"name": self.symmetric_link_without_code.name})

        with self.assertRaises(IntegrityError), self.env.cr.savepoint():
            self.LinkType.create(
                {
                    "name": self.symmetric_link_with_code.name + "test_8",
                    "code": self.symmetric_link_with_code.code,
                }
            )
        with self.assertRaises(IntegrityError), self.env.cr.savepoint():
            inverse_name = self.asymmetric_link_without_inverse_code.inverse_name
            self.LinkType.create(
                {
                    "name": self.asymmetric_link_without_inverse_code.name + "test_8",
                    "inverse_name": inverse_name,
                }
            )
        with self.assertRaises(IntegrityError), self.env.cr.savepoint():
            self.LinkType.create(
                {
                    "name": self.asymmetric_link_with_inverse_code.name + "test_8",
                    "inverse_name": self.asymmetric_link_with_inverse_code.inverse_name
                    + "test_8",
                    "inverse_code": self.asymmetric_link_with_inverse_code.inverse_code,
                }
            )
