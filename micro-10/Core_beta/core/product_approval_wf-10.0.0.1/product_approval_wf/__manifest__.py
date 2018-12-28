# -*- coding: utf-8 -*-
{
    "name": "Product Approval WorkFlow",
    "version": "0.1",
    "author": "Nilesh Sheliya",
    "category": "Product",
    "description": """
        This module will add state in the products, if products state is in draft, than it can't be salable and once it is confirmed, it becomes salable and can't modify by anyone.
product, products, approval, approve, product approval, workflow, work-flow, product workflow, product work-flow, product approval workflow, product approval workflow in odoo, product workflow in odoo, product approval in odoo
    """,
    "depends": ["product"],
    "price": 30.00,
    "currency": "EUR",
    "data": [
              "security/security.xml",
              "views/product_product.xml",
              "views/product_template.xml",
            ],
    "images": ['static/description/not-approved.png'],
    "installable": True,
    "auto_install": False,
    "application": True,
}
