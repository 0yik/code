# -*- coding: utf-8 -*-
{
    'name' : 'POS Show Qty Popup',
    'version' : '1.0',
    'category': 'Point of sale',
    'author': 'HashMicro / MP technolabs / Parikshit Vaghasiya',
    'description': """POS Show Qty Popup.
    """,
    'website': 'www.hashmicro.com',
    'depends' : ['base','point_of_sale'],
    'data': [
		'view/pos_show_qty_view.xml', 
    ],
    'demo': [
    ],
    'qweb': [
	# 'static/src/xml/*.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
