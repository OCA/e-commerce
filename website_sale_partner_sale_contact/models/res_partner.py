# Copyright 2026 ForgeFlow S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import models


class ResPartner(models.Model):
    _inherit = "res.partner"

    def _get_sale_contact_company(self):
        """Return the company to use as customer for this website partner.

        - Child contact of a company: the commercial (root) company.
        - Individual with a typed ``company_name`` but no company parent: find
          (by name) or create that company and link this contact under it.
        - Otherwise: an empty recordset (no split needed).
        """
        self.ensure_one()
        commercial = self.commercial_partner_id
        if commercial and commercial != self:
            return commercial
        if not self.is_company and self.company_name:
            company = self.search(
                [("is_company", "=", True), ("name", "=", self.company_name)],
                limit=1,
            )
            if not company:
                company = self.create({"name": self.company_name, "is_company": True})
            if self.parent_id != company:
                self.parent_id = company
            return company
        return self.browse()
