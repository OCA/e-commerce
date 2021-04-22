# Copyright 2021 Tecnativa - Jairo Llopis
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from urllib import parse
from odoo import _, api, fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    # Actually a One2one field due to a unique constraint on the other side
    survey_user_input_ids = fields.One2many(
        "survey.user_input",
        "sale_order_line_id",
        string="Survey answers",
        help="Answer filled by the buyer at checkout.",
    )
    survey_user_input_id = fields.Many2one(
        "survey.user_input",
        string="Survey answer",
        compute="_compute_survey_user_input_id",
        help="Answer filled by the buyer at checkout.",
    )

    @api.depends("survey_user_input_ids")
    def _compute_survey_user_input_id(self):
        """Mimic one2one field."""
        for one in self:
            one.survey_user_input_id = one.survey_user_input_ids

    def _survey_url(self):
        """Get URL to fill survey."""
        survey = self.product_id.survey_id.with_context(
            relative_url=True, survey_token=self.survey_user_input_ids.token
        )
        if not survey:
            return
        # Get survey URL
        scheme, netloc, path, query, fragment = parse.urlsplit(
            survey.action_print_survey()["url"]
            if self.survey_user_input_ids.state == "done"
            else survey.action_start_survey()["url"]
        )
        # Reformat it adding custom query string
        url = parse.urlunsplit(
            (
                scheme,
                netloc,
                path,
                query + "&sale_order_line_id=%d" % self.id,
                fragment,
            )
        )
        return url
