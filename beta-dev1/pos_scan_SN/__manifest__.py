# -*- coding: utf-8 -*-
{
    'name' : 'pos_scan_SN',
    'version' : '1.0',
    'category': 'Point of sale',
    'author': 'HashMicro / Viet',
    'description': """make the search product on pos can be able to do by scan the SN barcode
    """,
    'website': 'www.hashmicro.com',
    'depends' : ['base','point_of_sale'],
    'data': [
		'view/register.xml',
    ],
    'demo': [
    ],
    'qweb': [
	    'static/src/xml/*.xml',
    ],
}
