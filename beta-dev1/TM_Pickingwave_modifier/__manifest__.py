# -*- coding: utf-8 -*-
{
    'name': "TM_Pickingwave_modifier",

    'description': """
        Sale,Invoice
    """,
    'author': 'HashMicro / Viet',
    'website': 'www.hashmicro.com',

    'category': 'stock',
    'version': '1.0',

    'depends': ['stock_picking_wave'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/stock_picking_wave.xml',
    ],
    # only loaded in demonstration mode
    'qweb': [],
    'demo': [
    ],
}