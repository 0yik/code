# -*- coding: utf-8 -*-
{
    'name': "Laborindo Modifier Invoice Order",

    'description': """
        Timesheet
    """,
    'author': 'HashMicro / Quy',
    'website': 'www.hashmicro.com',

    'category': 'sale,invoice',
    'version': '1.0',

    'depends': ['account','sale'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        # 'views/employee_sequence.xml',
        'views/sale_to_invoice.xml',
    ],
    # only loaded in demonstration mode
    'qweb': [],
    'demo': [
    ],
}