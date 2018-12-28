# -*- coding: utf-8 -*-
{
    "name": """Inventory BOM Check""",
    "summary": """Inventory BOM Check""",
    "category": "Equipment",
    "images": [],
    "version": "10.0",
    "application": False,

    "author": "Hashmicro / Sang/ Janbaz Aga",
    "website": "https://hashmicro.com",
    "license": "AGPL-3",
    "depends": [
        'base', 'inventory_check','mrp'
    ],
    "qweb": ['static/src/xml/inventory_bom_check.xml'],
    "data": [
        "views/templates.xml",
        "views/inventory_check_view.xml",
    ],

    "auto_install": False,
    'application': True,
    "installable": True,
}
