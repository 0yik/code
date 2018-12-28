# -*- coding: utf-8 -*-
{
    'name' : 'Laborindo Modifier Multidiscount Purchase Order',
    'version' : '1.0',
    'category': 'purchase',
    'author': 'HashMicro / MP technolabs / Bipin Prajapati',
    'description': """Modify multi discount for purchase order
    """,
    'website': 'www.hashmicro.com',
    'depends' : ['purchase','account'],
    'data': [
        'views/purchase_view.xml',
        'views/invoice_view.xml',
    ],
    'demo': [

    ],
    'qweb': [

    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
