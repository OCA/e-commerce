{
    "name": "Website Delivery Group",
    "summary": "Provides a way to group shipping methods",
    "version": "14.0.1.0.0",
    "development_status": "Production/Stable",
    "category": "Website",
    "website": "https://github.com/OCA/e-commerce",
    "author": "Iván Todorovich, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "maintainers": [
        "ivantodorovich",
    ],
    "depends": [
        "website_sale_delivery",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/delivery_carrier.xml",
        "views/delivery_carrier_group.xml",
        "views/templates.xml",
    ],
    "demo": [
        "demo/demo.xml",
    ],
}
