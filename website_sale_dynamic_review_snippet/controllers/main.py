from odoo.http import Controller, request, route

from odoo.addons.mail.tools.discuss import Store


class CustomerReview(Controller):
    @route(
        ["/mail/review/messages"],
        methods=["POST"],
        type="json",
        auth="public",
        website=True,
    )
    def mail_review_messages(self, before=None, after=None, limit=30):
        domain = [
            ("model", "=", "product.template"),
            ("message_type", "=", "comment"),
            ("rating_value", ">=", 1),
            (
                "res_id",
                "in",
                request.env["product.template"]._search([("is_published", "=", True)]),
            ),
        ]
        result = (
            request.env["mail.message"]
            .sudo()
            ._message_fetch(domain, None, before, after, None, limit)
        )
        messages = result.pop("messages")
        messages_vals_list = messages.portal_message_format(
            options={"rating_include": True}
        )
        products = (
            request.env["product.template"]
            .sudo()
            .browse([vals["res_id"] for vals in messages_vals_list])
        )
        product_by_id = {product.id: product for product in products}
        for vals in messages_vals_list:
            product = product_by_id[vals["res_id"]]
            vals["thread"]["name"] = product.name
            vals["website_url"] = product.website_url
        return {
            **result,
            "data": {
                "mail.message": messages_vals_list,
            },
            "messages": Store.many_ids(messages),
        }

    @route("/portal/review_init", type="json", auth="public", website=True)
    def portal_review_init(self, **kwargs):
        store = Store()
        request.env["res.users"]._init_store_data(store)
        if request.env.user.has_group("website.group_website_restricted_editor"):
            store.add(request.env.user.partner_id, {"is_user_publisher": True})
        reviewed_products = (
            request.env["mail.message"]
            .sudo()
            ._search(
                [
                    ("model", "=", "product.template"),
                    ("message_type", "=", "comment"),
                    ("rating_value", ">=", 1),
                ]
            )
        )
        products = request.env["product.template"].search(
            [
                ("is_published", "=", True),
                ("id", "in", reviewed_products.subselect("DISTINCT res_id")),
            ]
        )
        product_obj = request.env["product.template"]
        for product in products:
            thread = product_obj._get_thread_with_access(product.id, **kwargs)
            if thread:
                mode = product_obj._get_mail_message_access([product.id], "create")
                has_react_access = product_obj._get_thread_with_access(
                    product.id, mode, **kwargs
                )
                can_react = has_react_access
                store.add(
                    thread,
                    {
                        "can_react": bool(can_react),
                        "hasReadAccess": thread.sudo(False).has_access("read"),
                    },
                    as_thread=True,
                )
        return store.get_result()
