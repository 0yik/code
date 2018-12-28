# -*- coding: utf-8 -*-

{
    'name': 'Account Journal Entry Base on Currency',
    'version': '2.0',
    'author': "HashMicro / MPTechnolabs - Komal Kaila",
    'category': 'Accounting',
    'sequence': 10,
    'summary': 'Journal Entry for Teo Garment',
    'description': """
        Journal Entry for Teo Garment
       """,
    'website': 'https://www.hashmicro.com',
    'depends': ['account'],
    'data': [
    'views/account_move_view.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
