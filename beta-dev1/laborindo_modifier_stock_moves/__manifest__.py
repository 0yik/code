# -*- coding: utf-8 -*-
{
    'name': "Laborindo Modifier Stock Move",

    'description': """
        Stock Move
    """,
    'author': 'HashMicro / Quy',
    'website': 'www.hashmicro.com',

    'category': 'stock',
    'version': '1.0',

    'depends': ['stock'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/stock_move.xml'
    ],
    # only loaded in demonstration mode
    'qweb': [],
    'demo': [
    ],
}