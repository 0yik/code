# -*- coding: utf-8 -*-
{
    'name': 'COA Parent',
    'category': 'Account',
    'summary': 'Parent account mapping in CoA',
    'description': 'Adding support to link parent account in CoA',
    'sequence': 15,
    'author': 'HashMicro/Saravanakumar',
    'website': 'www.hashmicro.com',
    'version': '1.0',
    'depends': ['account'],
    'data': [
        'views/account_view.xml',
    ],
    'installable': True,
    'application': True,
}
