from urllib.parse import urlparse

from odoo.tests.common import HttpCase


class TestWebsiteSaleRequireLogin(HttpCase):
    def setUp(self):
        super().setUp()
        self.guest_user = self.env.ref("base.public_user")
        self.logged_in_user = self.env["res.users"].create(
            {
                "name": "Test User",
                "login": "testuser@example.com",
                "email": "testuser@example.com",
                "password": "password",
            }
        )

    def test_guest_checkout_redirection(self):
        """Test if guest user is redirected to login when accessing checkout."""
        response = self.url_open("/shop/checkout")
        redirect_url = urlparse(response.url).path
        self.assertEqual(
            redirect_url,
            "/web/login",
            "Guest should be redirected to login when accessing checkout.",
        )

    def test_logged_in_checkout_access(self):
        """Test if logged-in user is not redirected when accessing checkout."""
        self.authenticate(self.logged_in_user.login, "password")
        response = self.url_open("/shop/checkout")
        self.assertNotEqual(
            response.url,
            "/web/login",
            "Logged-in user should not be redirected when accessing checkout.",
        )

    def test_guest_address_redirection(self):
        """Test if guest user is redirected to login when accessing address."""
        response = self.url_open("/shop/address")
        redirect_url = urlparse(response.url).path
        self.assertEqual(
            redirect_url,
            "/web/login",
            "Guest should be redirected to login when accessing address.",
        )

    def test_logged_in_address_access(self):
        """Test if logged-in user is not redirected when accessing address."""
        self.authenticate(self.logged_in_user.login, "password")
        response = self.url_open("/shop/address")
        self.assertNotEqual(
            response.url,
            "/web/login",
            "Logged-in user should not be redirected when accessing address.",
        )
