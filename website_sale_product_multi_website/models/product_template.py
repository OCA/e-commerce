# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, fields, models
from odoo.fields import Domain


class ProductTemplate(models.Model):
    _inherit = "product.template"

    website_ids = fields.Many2many(
        "website",
        "product_template_website_rel",
        "product_template_id",
        "website_id",
        string="Websites",
        # restrict, like the foreign key of the website_id this replaces:
        # cascading would silently empty website_ids when a website is
        # deleted, and an empty website_ids publishes the product on every
        # remaining website instead of none.
        ondelete="restrict",
        help="Restrict the product to the selected websites. Leave empty to "
        "make it available on all websites.",
    )
    website_id = fields.Many2one(
        "website",
        compute="_compute_website_id",
        inverse="_inverse_website_id",
        search="_search_website_id",
        store=False,
    )

    @api.depends("website_ids")
    @api.depends_context("website_id")
    def _compute_website_id(self):
        # The core reads website_id to decide whether a record belongs to the
        # website being browsed: ir.http._pre_dispatch() returns a 404 when it
        # differs, and _compute_website_published() unpublishes it. Answer with
        # the current website whenever the product is assigned to it, so a
        # product on several websites matches on each one instead of only on
        # the first. sudo(): website_ids is not readable by the public user,
        # and this is also evaluated in memory by filtered_domain() on the
        # accessory and alternative products.
        current_website_id = self.env.context.get("website_id")
        for record in self:
            website_ids = record.sudo().website_ids
            record.website_id = (
                current_website_id
                if current_website_id in website_ids.ids
                else website_ids[:1].id
            )

    def _inverse_website_id(self):
        for record in self:
            if record.website_id and record.website_id not in record.website_ids:
                record.website_ids = [(4, record.website_id.id)]

    def _search_website_id(self, operator, value):
        # Same reason as the compute: the core restricts records through
        # website_id (website_domain(), _search_website_published()), while
        # here the restriction lives in website_ids.
        if operator != "in":
            # Anything else (a custom filter on the website name, a path such
            # as website_id.company_id) reads the same on website_ids.
            return Domain("website_ids", operator, value)
        # An empty website_ids means the product is available on every
        # website, which is what website_id being unset used to mean.
        website_ids = [website_id for website_id in value if website_id]
        domain = (
            Domain("website_ids", "in", website_ids) if website_ids else Domain.FALSE
        )
        if False in value:
            domain |= Domain("website_ids", "=", False)
        return domain
