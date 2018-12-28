# -*- coding: utf-8 -*-
{
    'name': "tm_inventory_low_stock",

    'description': """
        Inventory
    """,
    'author': 'HashMicro / Viet',
    'website': 'www.hashmicro.com',

    'category': 'inventory',
    'version': '1.0',

    'depends': ['stock'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/stock.xml',
    ],
    # only loaded in demonstration mode
    'qweb': [],
    'demo': [
    ],
}