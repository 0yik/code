# -*- coding: utf-8 -*-
{
    'name' : 'Laborindo Department',
    'version' : '1.0',
    'category': '',
    'author': 'HashMicro / Abulkasim Kazi',
    'description': """ """,
    'website': 'www.hashmicro.com',
    'depends' : ['account_accountant', 'account_voucher'],
    'data': [
        'security/ir.model.access.csv',
        'views/res_department_view.xml',
        'views/account_view.xml',
    ],
    'demo': [],
    'qweb': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}
