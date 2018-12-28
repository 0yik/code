# -*- coding: utf-8 -*-
{
    'name' : 'POS Tax Branch',
    'version' : '1.0',
    'category': 'Point of sale',
    'author': 'HashMicro / Viet',
    'description': """POS Tax Branch
    """,
    'website': 'www.hashmicro.com',
    'depends' : ['base','point_of_sale'],
    'data': [
		'view/register.xml',
        'view/pos_tax_branch.xml'
    ],
    'demo': [
    ],
    'qweb': [
	    'static/src/xml/*.xml',
    ],
}
