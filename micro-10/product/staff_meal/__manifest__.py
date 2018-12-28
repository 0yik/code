# -*- coding: utf-8 -*-
{
    'name' : 'Staff Meal',
    'version' : '1.0',
    'category': 'pos',
    'author': 'HashMicro / MP technolabs - Komal Kaila / Saravanakumar',
    'description': """This module intends to have a functionality of free order.
    """,
    'website': 'www.hashmicro.com',
    'depends' : ['base','pizzahut_modifier_startscreen','pos_restaurant_kitchen','pos_to_sales_order','sms_whatsapp_api_config'],
    'data': [ 
        'views/pos_all_free_template.xml',
        'views/pos_all_free_view.xml'
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
