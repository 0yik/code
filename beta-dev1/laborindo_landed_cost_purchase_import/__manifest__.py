# -*- coding: utf-8 -*-
{
    'name' : 'Laborindo Landed Cost Purchase Import',
    'version' : '1.0',
    'category': 'purchase',
    'author': 'HashMicro / MP technolabs / Bipin Prajapati',
    'description': """Enter landed cost in purchase order
    """,
    'website': 'www.hashmicro.com',
    'depends' : ['purchase','account', 'stock','stock_landed_costs'],
    'data': [
        'wizard/landed_cost_view.xml',
        'views/purchase_view.xml',

    ],
    'demo': [

    ],
    'qweb': [

    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
