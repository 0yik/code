# -*- coding: utf-8 -*-
{
    'name': "laborindo modifier fiscal",

    'description': """
       Added New field in Inventory  Valuation
    """,
    'author': 'HashMicro / Viet',
    'website': 'www.hashmicro.com',

    'category': 'Stock',
    'version': '1.0',

    # any module necessary for this one to work correctly
    'depends': ['base','account','sale'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}