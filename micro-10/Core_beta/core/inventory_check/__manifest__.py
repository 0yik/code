# -*- coding: utf-8 -*-
{
    "name": """Inventory Check""",
    "summary": """Inventory Check""",
    "category": "Equipment",
    "images": [],
    "version": "10.0",
    "application": False,

    "author": "Hashmicro / Duy",
    "website": "https://hashmicro.com",
    "license": "AGPL-3",
    "depends": [
        'stock','purchase'
    ],
    "qweb": ['static/src/xml/inventory_check_quickadd.xml'],
    "data": [
        "views/templates.xml",
        "views/inventory_check_view.xml",
    ],

    "auto_install": False,
    'application': True,
    "installable": True,
}
