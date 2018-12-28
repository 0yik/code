# -*- coding: utf-8 -*-
{
    'name': "TrueMoney Modifier Repairs",

    'description': """
        Repair Order
    """,
    'author': 'HashMicro / Quy',
    'website': 'www.hashmicro.com',

    'category': 'repair',
    'version': '1.0',

    'depends': ['mrp_repair'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        # 'views/employee_sequence.xml',
        'views/repair_order.xml',
    ],
    # only loaded in demonstration mode
    'qweb': [],
    'demo': [
    ],
}