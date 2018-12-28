# -*- coding: utf-8 -*-
{
    'name': 'Aged Partner Balances',
    'version': '1.0',
    'category': 'Accounting',
    'sequence': 15,
    'summary': 'setup for aged partner balance report',
    'description': "This module includes aged partner balance report related setup",
    'website': 'http://www.hashmicro.com/',
    'author': 'Hashmicro/Saravanakumar',
    'depends': [
        'account_accountant'
    ],
    'data': [
        'views/partner_view.xml',
        'wizard/aged_partner_balance_xl.xml',
        'report/account_view.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}