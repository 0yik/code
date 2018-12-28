# -*- coding: utf-8 -*-
{
    'name': "Purchase Order Expiry",

    'description': """
        Purchase
    """,
    'author': 'HashMicro / Quy',
    'website': 'www.hashmicro.com',

    'category': 'purchase',
    'version': '1.0',

    'depends': ['purchase'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/purchase_order.xml'
    ],
    # only loaded in demonstration mode
    'qweb': [],
    'demo': [
    ],
}