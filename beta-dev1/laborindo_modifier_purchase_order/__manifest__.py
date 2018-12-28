# -*- coding: utf-8 -*-
{
    'name': "Laborindo Modifier Purchase Order",

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
        # 'views/employee_sequence.xml',
        'views/sequence.xml',
        'views/modification_purchase_order.xml'
    ],
    # only loaded in demonstration mode
    'qweb': [],
    'demo': [
    ],
}