# -*- coding: utf-8 -*-
{
    'name': "TM Sale Modifier",

    'description': """
        Sale,Invoice
    """,
    'author': 'HashMicro / Quy',
    'website': 'www.hashmicro.com',

    'category': 'sale,invoice',
    'version': '1.0',

    'depends': ['account','sale'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/invoice.xml',
        'views/sale_order.xml',
    ],
    # only loaded in demonstration mode
    'qweb': [],
    'demo': [
    ],
}