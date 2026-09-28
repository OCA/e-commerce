from odoo.tests.common import HttpCase, tagged


@tagged("post_install", "-at_install")
class TestMailReviewMessages(HttpCase):
    def test_public_route_hides_unpublished_product_reviews(self):
        published = self.env["product.template"].create(
            {"name": "Published Review Product", "is_published": True}
        )
        unpublished = self.env["product.template"].create(
            {"name": "Unpublished Review Product", "is_published": False}
        )
        published_message = published.message_post(
            body="Visible review",
            message_type="comment",
            rating_value="5",
            subtype_xmlid="mail.mt_comment",
        )
        unpublished_message = unpublished.message_post(
            body="Hidden review",
            message_type="comment",
            rating_value="1",
            subtype_xmlid="mail.mt_comment",
        )
        self.env.cr.flush()

        # No login: the route is auth="public" and fetches messages with sudo().
        result = self.make_jsonrpc_request("/mail/review/messages", {"limit": 30})
        messages = result["data"]["mail.message"]
        message_ids = {message["id"] for message in messages}
        res_ids = {message["res_id"] for message in messages}

        self.assertIn(published_message.id, message_ids)
        self.assertIn(published.id, res_ids)
        self.assertNotIn(unpublished_message.id, message_ids)
        self.assertNotIn(unpublished.id, res_ids)
        self.assertFalse(
            any(
                message.get("body") and "Hidden review" in message["body"]
                for message in messages
            )
        )
