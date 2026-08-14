# Copyright 2026 Tecnativa - Pilar Vargas
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


def post_init_hook(env):
    booking_step = env.ref("website_sale_resource_booking.checkout_step_booking")
    for website in env["website"].search([]):
        booking_step.copy(
            {
                "website_id": website.id,
                "is_published": True,
            }
        )
