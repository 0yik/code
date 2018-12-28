# -*- coding: utf-8 -*-
{
    'name': 'Percentage Incoming Product',
    'version': '1.0',
    'category': 'Purchase',
    'sequence': 18,
    'summary': 'setup for received quantity percentage calculation.',
    'description': "This module includes percentage calculation for received quanity.",
    'website': 'http://www.hashmicro.com/',
    'author': 'Hashmicro/Kannan',
    'depends': ['purchase'],
    'data': [
        'views/stock_move_view.xml'
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}