# -*- coding: utf-8 -*-
{
    'name': "TrueMoney Repair Report",

    'description': """
        Repair Order Report
    """,
    'author': 'HashMicro / Quy',
    'website': 'www.hashmicro.com',

    'category': 'repair',
    'version': '1.0',

    'depends': ['mrp_repair','product'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        # 'views/employee_sequence.xml',
        'views/mrp_repair_report.xml',
    ],
    # only loaded in demonstration mode
    'qweb': [],
    'demo': [
    ],
}