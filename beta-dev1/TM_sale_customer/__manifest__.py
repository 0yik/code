# -*- coding: utf-8 -*-
{
    'name': "TM Sale Customer",

    'description': """
        Customer
    """,
    'author': 'HashMicro / Quy',
    'website': 'www.hashmicro.com',

    'category': 'sale,invoice',
    'version': '1.0',

    'depends': ['base','sale'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/res_partner.xml',
    ],
    # only loaded in demonstration mode
    'qweb': [],
    'demo': [
    ],
}