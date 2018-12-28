# -*- coding: utf-8 -*-
{
    'name' : 'Dine in product order category filter',
    'version' : '1.0',
    'category': 'pos',
    'author': 'HashMicro / MP technolabs - Parikshit Vaghasiya',
    'description': """This module create product order category to filter product in pos.
    """,
    'website': 'www.hashmicro.com',
    'depends' : ['base', 'point_of_sale', 'pos_restaurant', 'pizzahut_modifier_startscreen', 'assign_temp_order'],
    'data': [ 
        'views/dinein_order_categ_template.xml',
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
