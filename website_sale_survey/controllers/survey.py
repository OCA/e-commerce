# Copyright 2021 Tecnativa - Jairo Llopis
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from contextlib import suppress
from logging import getLogger
from odoo import _
from odoo.exceptions import ValidationError
from odoo.http import request, route
from ...survey.controllers import main

_logger = getLogger(__name__)


class Survey(main.Survey):
    @route()
    def start_survey(self, survey, token=None, sale_order_line_id=None, **post):
        """Link survey answers to sale order lines."""
        # No order line? Nothing special to do here...
        if not sale_order_line_id:
            return super().start_survey(survey, token, **post)
        line = request.env["sale.order.line"].sudo().browse(int(sale_order_line_id))
        order = request.website.sale_get_order()
        if line not in order.order_line:
            # Trying to edit others' lines? Bad boy...
            raise ValidationError(
                _("You can only answer to surveys from lines in your current cart.")
            )
        if not token and line.survey_user_input_ids.token:
            # OK, let me explain... Imagine the user clicks on "Fill survey",
            # then lands here and a survey.user_input is created and linked to
            # that sale order line; then he clicks on browser's "Back" button
            # and goes back to the browser's cached version of the cart (which
            # doesn't know there's an already-linked user input), and then
            # clicks again on "Fill survey", which leads here again without
            # token (although if he just pressed F5 back in the cart, he'd have
            # the token). Well, we can safely assume that, if he's giving us a
            # `sale_order_line_id` from his own cart, he should have access to
            # the token already anyway, so we modify it here to let him
            # continue without problem.
            token = line.survey_user_input_ids.token
        result = super().start_survey(survey, token, **post)
        # Without qcontext or token, can't update it
        with suppress(KeyError, AttributeError):
            user_input = (
                request.env["survey.user_input"]
                .sudo()
                .search([("token", "=", result.qcontext["token"])], limit=1)
            )
            user_input.sale_order_line_id = line
        return result
