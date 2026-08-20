# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import models
from odoo.fields import Domain


class Website(models.Model):
    _inherit = "website"

    def website_domain(self):
        # Keep the standard behavior by default, but allow specific flows to switch
        # the website restriction from website_id to website_ids through context.
        if self.env.context.get("multi_website_domain"):
            target_website_ids = self.ids

            def to_sql(model, alias, query):
                domain = Domain("website_ids", "=", False) | Domain(
                    "website_ids", "in", target_website_ids
                )
                # Full optimization is needed to turn the '=' False leaf into
                # something the many2many field can translate to SQL, the same
                # processing regular searches apply before calling _to_sql().
                return domain.optimize_full(model)._to_sql(model, alias, query)

            # Unlike website_id, website_ids has no SQL column of its own, so
            # a plain Domain evaluated in-memory (e.g. filtered_domain(), used
            # by core accessory/alternative product logic) would fetch it
            # directly and raise an AccessError for products a public user
            # can't otherwise read. Domain.custom() without a predicate makes
            # that in-memory evaluation run through a real search() instead,
            # which applies ir.rule the same safe way regular searches do.
            return Domain.custom(to_sql=to_sql)
        return super().website_domain()

    def sale_product_domain(self):
        # Reuse the standard published search while enabling the multi-website
        # variant of website_domain() used in website sale flows.
        return super(
            Website, self.with_context(multi_website_domain=True)
        ).sale_product_domain()
