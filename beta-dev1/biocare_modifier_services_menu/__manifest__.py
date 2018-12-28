# -*- coding: utf-8 -*-
{
    "name": """Biocare Service""",
    "summary": """Biocare Service To list out the all service products""",
    "category": "Sales",
    "images": [],
    "version": "10.0",
    "application": False,

    "author": "Hashmicro / Krupesh",
    "website": "https://hashmicro.com",
    "license": "AGPL-3",
    "depends": [
        'product','sales_team', 'sale',
    ],
    "data": [
        'views/product_view.xml',
    ],

    "auto_install": False,
    'application': True,
    "installable": True,
}
