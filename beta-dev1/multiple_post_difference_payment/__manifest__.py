# -*- coding: utf-8 -*-
{
    'name': "multiple_post_difference_payment",

    'description': """
        Multiple_post_difference_payment
    """,
    'author': 'HashMicro / Viet/ Abulkasim Kazi',
    'website': 'www.hashmicro.com',

    'category': 'timesheet',
    'version': '1.0',

    'depends': ['account_accountant'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        # 'views/employee_sequence.xml',
        'views/views.xml',
    ],
    # only loaded in demonstration mode
    'qweb': [],
    'demo': [
    ],
}