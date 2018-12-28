# -*- coding: utf-8 -*-
{
    'name': "TM Sale Config Modifier",

    'description': """
        Sale,Invoice
    """,
    'author': 'HashMicro / Viet',
    'website': 'www.hashmicro.com',

    'category': 'sale,invoice',
    'version': '1.0',

    'depends': ['account','sale'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/sale_config.xml',
    ],
    # only loaded in demonstration mode
    'qweb': [],
    'demo': [
    ],
}