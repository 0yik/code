# -*- coding: utf-8 -*-
{
    'name': "laborindo_adjustment_bybrand",

    
    'description': """
        Inventory adjustment by brand
    """,

    'author': "Hashmicro / MpTechnolabs - Prakash",
    'website': "www.hashmicro.com",

    
    'category': 'Inventory',
    'version': '1.0',

    # any module necessary for this one to work correctly
    'depends': ['base','stock'],

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