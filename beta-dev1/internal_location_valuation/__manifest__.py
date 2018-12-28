# -*- coding: utf-8 -*-
{
    'name' : 'Internal Location Valuation',
    'version' : '1.0',
    'category': 'Inventory',
    'author': 'HashMicro / MP Technolabs - Parikshit Vaghasiya',
    'description': 'This module will add internal location filter on stock move.',
    'website': 'www.hashmicro.com',
    'depends' : [ 'stock'],
    'data': [
        'views/stock_picking_views.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
