# -*- coding: utf-8 -*-
{
    'name' : 'PDP Modifier Customer',
    'version' : '1.0',
    'category': 'Customer',
    'author': 'HashMicro / MP technolabs / Monali',
    'description': """
	VO Change list view menu, new project amount calculation error.
    """,
    'website': 'www.hashmicro.com',
    'depends' : [
	'base','sale'
    ],
    'data': [
	'data/partner_sequence.xml',
	'views/res_partner_view.xml',
    ],
    'demo': [
    ],
    'qweb': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}
