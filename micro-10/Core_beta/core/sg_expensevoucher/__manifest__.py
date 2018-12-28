# -*- coding: utf-8 -*-
{
    'name': 'Sg Expensevoucher',
    'version': '1.0',
    'category': 'Accounting',
    'sequence': 19,
    'summary': 'setup to customize account voucher',
    'description': "This module includes setup to customize account voucher and change menu name",
    'website': 'http://www.hashmicro.com/',
    'author': 'Hashmicro/Kannan, Goutham',
    'depends': [
        'account_voucher'
    ],
    'data': [
        'views/account_voucher_view.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}