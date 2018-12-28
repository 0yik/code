# -*- coding: utf-8 -*-
{
    'name' : 'Aikchin Modifier Pos Issuer',
    'version' : '1.0',
    'category': 'Point Of Sale',
    'author': 'HashMicro / MP technolabs / Monali',
    'description': """
    """,
    'website': 'www.hashmicro.com',
    'depends' : [
	'point_of_sale','hr',
    ],
    'data': [
	'views/pos_issuer_templates.xml',
    ],
    'demo': [
    ],
    'qweb': ['static/src/xml/pos.xml'],
    'installable': True,
    'application': True,
    'auto_install': False,
}
