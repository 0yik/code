# -*- coding: utf-8 -*-
{
    'name': 'Group Chartofaccounts',
    'version': '1.0',
    'category': 'Accounting',
    'sequence': 15,
    'summary': 'Setup to view consolidated chart of accounts in multi-company',
    'description': "This module includes setup which Allows to view consolidated chart of accounts in multi-company (Group Company) environment",
    'website': 'http://www.hashmicro.com/',
    'author': 'Hashmicro/Saravana Kumar',
    'depends': [
        'sg_account_report'
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/account_view.xml',
        'views/res_company_view.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}