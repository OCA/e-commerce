# Copyright 2020 Tecnativa - David Vidal
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)
from odoo import api, fields, models
from odoo.fields import Domain


class ProductBrand(models.Model):
    _name = "product.brand"
    _inherit = [
        "product.brand",
        "image.mixin",
        "website.published.multi.mixin",
        "website.searchable.mixin",
        "website.seo.metadata",
    ]

    cover_image = fields.Image(max_width=2560, max_height=2560)
    website_description = fields.Html(translate=True)
    website_footer = fields.Html(translate=True)
    show_brand_name = fields.Boolean(default=True)
    show_brand_description = fields.Boolean(default=True)
    show_without_published_products = fields.Boolean(default=False)
    align_brand_content = fields.Selection(
        selection=[
            ("left", "Left"),
            ("center", "Center"),
        ],
        default="left",
        required=True,
    )
    published_products_count = fields.Integer(
        compute="_compute_published_products_count",
    )

    def _default_is_published(self):
        return True

    @api.depends("name")
    def _compute_website_url(self):
        res = super()._compute_website_url()
        for brand in self:
            brand.website_url = f"/shop/brand/{self.env['ir.http']._slug(brand)}"
        return res

    def _compute_published_products_count(self):
        for brand in self:
            brand.published_products_count = self.env["product.template"].search_count(
                [
                    ("product_brand_id", "=", brand.id),
                    ("website_published", "=", True),
                ]
            )

    @api.model
    def _website_scope_domain(self, website=None):
        website = website or self.env["website"].get_current_website()
        website_id = website.id if website else False
        return Domain.OR(
            [
                Domain("website_id", "=", False),
                Domain("website_id", "=", website_id),
            ]
        )

    @api.model
    def _website_public_domain(self, website=None):
        domain = Domain("website_published", "=", True)
        domain &= self._website_scope_domain(website=website)
        return domain

    @api.model
    def _search_get_detail(self, website, order, options):
        with_image = options.get("displayImage")
        with_description = options.get("displayDescription")
        domains = [self._website_public_domain(website=website)]
        search_fields = ["name"]
        fetch_fields = ["id", "name", "website_url"]
        mapping = {
            "name": {"name": "name", "type": "text", "match": True},
            "website_url": {"name": "website_url", "type": "text", "truncate": False},
        }
        if with_description:
            search_fields.append("website_description")
            fetch_fields.append("website_description")
            mapping["description"] = {
                "name": "website_description",
                "type": "text",
                "match": True,
                "html": True,
            }
        if with_image:
            mapping["image_url"] = {"name": "image_url", "type": "html"}

        return {
            "model": "product.brand",
            "base_domain": domains,
            "search_fields": search_fields,
            "fetch_fields": fetch_fields,
            "mapping": mapping,
            "icon": "fa-tags",
            "order": "name desc, id desc"
            if "name desc" in order
            else "name asc, id desc",
        }

    def _search_render_results(self, fetch_fields, mapping, icon, limit):
        results_data = super()._search_render_results(
            fetch_fields, mapping, icon, limit
        )
        if "image_url" in mapping:
            for data in results_data:
                data["image_url"] = f"/web/image/product.brand/{data['id']}/image_128"
        return results_data
