# -*- coding: utf-8 -*-
{
    'name' : 'POS Order From',
    'version' : '1.0',
    'category': 'Point Of Sale',
    'author': 'HashMicro / MP technolabs / Purvi Pandya',
    'description': """POS Order From.
    """,
    'website': 'www.hashmicro.com',
    'depends' : ['base', 'point_of_sale', 'pos_bus'],
    'data': [
        'view/pos_order_view.xml',
        'view/template.xml',
    ],
    'demo': [
        
    ],
    'qweb': [
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
