# -*- coding: utf-8 -*-
{
    'name' : 'Laborindo Down Payment Purchase Order',
    'version' : '1.0',
    'category': 'purchase',
    'author': 'HashMicro / MP technolabs / Bipin Prajapati',
    'description': """Laborindo Down Payment Purchase Order
    """,
    'website': 'www.hashmicro.com',
    'depends' : ['purchase','account'],
    'data': [
        'wizard/purchase_make_invoice_advance_views.xml',
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
