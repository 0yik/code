# -*- coding: utf-8 -*-
{
    'name' : 'POS Complimentary Discount',
    'version' : '1.0',
    'category': 'pos',
    'author': 'HashMicro / MP technolabs - Komal Kaila',
    'description': """When the button is clicked, the price section of the highlighted menu will be changed to ‘Complimentary’ and the item price along with it tax and service charge will not be included in total.
    """,
    'website': 'www.hashmicro.com',
    'depends' : ['base','point_of_sale'],
    'data': [ 
        'views/pos_complimentary_registration.xml',
        'views/pos_order_view.xml',
    ],
    'demo': [
    ],
    'qweb': [
	   'static/src/xml/*.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
