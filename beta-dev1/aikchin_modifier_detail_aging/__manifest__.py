# -*- coding: utf-8 -*-
{
    'name': 'Aikchin Modifier Detail Aging',
    'version': '1.0',
    'category': 'Account',
    'summary': '',
    'description': "Modify Printout Title Aged Partner Balance to Detail Aging Report",
    'website': 'https://www.hashmicro.com',
    'author': 'HashMicro / MP technolabs / Monali',
    'depends': ['account'],
    'data': [
        'views/aging_detailed.xml',
		'views/menu.xml',
    ],
    'qweb': [

    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
