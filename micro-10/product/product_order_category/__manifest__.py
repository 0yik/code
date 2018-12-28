# -*- coding: utf-8 -*-
{
    'name' : 'Product Order Category',
    'version' : '1.0',
    'category': 'pos',
    'author': 'HashMicro / MP technolabs - Parikshit Vaghasiya',
    'description': """This module create product order category to filter product in pos.
    """,
    'website': 'www.hashmicro.com',
    'depends' : ['base','pizzahut_modifier_startscreen','pos_restaurant_kitchen','pos_to_sales_order','staff_meal','delivery_orders_kds'],
    'data': [ 
        'security/ir.model.access.csv',
        'views/pos_order_categ_template.xml',
        'data/pos_order_categ_data.xml'
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
