# -*- coding: utf-8 -*-
{
    'name': 'PDP Modifier Purchase',
    'version': '1.0',
    'category': 'Purchase',
    'sequence': 15,
    'summary': 'setup for unreceived quantity calculation.',
    'description': "This module includes calculation for unreceived quantity based on actual and received quantity.",
    'website': 'http://www.hashmicro.com/',
    'author': 'Hashmicro/Kannan / MP Technolabs / Vatsal',
    'depends': ['purchase','branch'],
    'data': [
        'views/purchase_order_view.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
