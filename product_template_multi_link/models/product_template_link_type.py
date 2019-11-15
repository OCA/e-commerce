# Copyright 2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ProductTemplateLinkType(models.Model):

    _name = "product.template.link.type"
    _description = "Product Template Link Type"

    name = fields.Char(required=True, translate=True)
    inverse_name = fields.Char(
        compute="_compute_inverse_name",
        inverse="_inverse_inverse_name",
        readonly=False,
        store=True,
        translate=True,
    )
    manual_inverse_name = fields.Char()
    is_symmetric = fields.Boolean(
        help="The relation meaning is the same from each side of the relation",
        default=True,
    )
    code = fields.Char(
        "Technical code",
        help="This code allows to provide a technical code to external"
        "systems identifying this link type",
    )
    inverse_code = fields.Char(
        "Technical code (inverse)",
        compute="_compute_inverse_code",
        inverse="_inverse_inverse_code",
        readonly=False,
        store=True,
        help="This code allows to provide a technical code to external"
        "systems identifying this link type",
    )
    manual_inverse_code = fields.Char()
    _sql_constraints = [
        ("name_uniq", "unique (name)", "Link type name already exists !"),
        (
            "inverse_name_uniq",
            "unique (inverse_name)",
            "Link type inverse name already exists !",
        ),
        (
            "code_uniq",
            "EXCLUDE (code WITH =) WHERE (code is not null)",
            "Link code already exists !",
        ),
        (
            "inverse_code_uniq",
            "EXCLUDE (inverse_code WITH =) WHERE (inverse_code is not null)",
            "Link inverse code already exists !",
        ),
    ]

    display_name = fields.Char(compute="_compute_display_name")

    def _inverse_inverse_name(self):
        for record in self:
            record.manual_inverse_name = record.inverse_name

    def _inverse_inverse_code(self):
        for record in self:
            record.manual_inverse_code = record.inverse_code

    @api.depends("name", "inverse_name")
    def _compute_display_name(self):
        for record in self:
            display_name = record.name
            if not record.is_symmetric:
                display_name = "{} / {}".format(record.inverse_name, record.name)
            record.display_name = display_name

    @api.depends("name", "is_symmetric")
    def _compute_inverse_name(self):
        for record in self:
            if record.is_symmetric:
                record.inverse_name = record.name
            else:
                record.inverse_name = record.manual_inverse_name

    @api.depends("code", "is_symmetric")
    def _compute_inverse_code(self):
        for record in self:
            if record.is_symmetric:
                record.inverse_code = record.code
            else:
                record.inverse_code = record.manual_inverse_code

    def write(self, vals):
        if not self:
            return True
        r = True
        for record in self:
            is_symmetric = vals.get("is_symmetric", record.is_symmetric)
            v = vals.copy()
            if is_symmetric:
                v.pop("inverse_code", None)
                v.pop("inverse_name", None)
            r = super(ProductTemplateLinkType, record).write(v)
        return r

    def get_by_code(self, code):
        """Get link matching given code.

        Just a shortcut for a search that can be done very often.
        """
        return self.search([("code", "=", code)], limit=1)
