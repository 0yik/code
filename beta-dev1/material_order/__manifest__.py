# -*- coding: utf-8 -*-
{
    "name": "Material Order",
    "author": "HashMicro/Quy",
    "version": "10.0.1.0",
    "website": "www.hashmicro.com",
    "category": "Purchase Management",
    "depends": ["purchase"],
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
