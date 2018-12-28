# -*- coding: utf-8 -*-
{
    'name': "Laborindo Report Delivery Note",

    'description': """
        Delivery Note
    """,
    'author': 'HashMicro / Quy',
    'website': 'www.hashmicro.com',

    'category': 'delivery',
    'version': '1.0',

    'depends': ['account','sale'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        # 'views/employee_sequence.xml',
        'views/delivery_note.xml',
    ],
    # only loaded in demonstration mode
    'qweb': [],
    'demo': [
    ],
}