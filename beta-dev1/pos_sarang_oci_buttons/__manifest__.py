# -*- coding: utf-8 -*-
{
    'name' : 'POS Sarang oci Buttons',
    'version' : '1.0',
    'category': 'Point Of Sale',
    'author': 'HashMicro / MP technolabs / Mital',
    'description': """POS Sarang oci Buttons.
    """,
    'website': 'www.hashmicro.com',
    'depends' : ['base', 'pos_restaurant_kitchen'],
    'data': [
		#'view/res_partner_view.xml', 
    ],
    'demo': [
    ],
    'qweb': [
	'static/src/xml/waiter_screen_inherit.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
