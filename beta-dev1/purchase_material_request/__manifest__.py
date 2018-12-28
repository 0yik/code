# -*- coding: utf-8 -*-
{
    "name": "Purchase Material Request",
    "author": "HashMicro",
    "version": "10.0.1.0",
    "website": "www.hashmicro.com",
    "category": "Purchase Management",
    "depends": ["brand_sales_report"],
    "data": [
        "security/ir.model.access.csv",
        "views/purchase_material_request_sequence.xml",
        "views/purchase_material_request_view.xml",
        "views/stock_move_view.xml"
    ],
    'demo': [
    ],
    "installable": True,
    "auto_install": False,
    "application": True,
}
