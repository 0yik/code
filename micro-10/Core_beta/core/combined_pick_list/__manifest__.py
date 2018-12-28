# -*- coding: utf-8 -*-
{
    'name': 'Combined Pick List',
    'version': '1.0',
    'category': 'Stock',
    'sequence': 16,
    'summary': 'Consolidated picking list by Product to ease operation.',
    'description': "This module includes setup to create pick list when delivery order is created and remove when delivery order moves to done state",
    'website': 'http://www.hashmicro.com/',
    'author': 'Hashmicro/Kannan',
    'depends': ['stock','stock_picking_wave'],
    'data': [
        'security/ir.model.access.csv',
        'views/pick_list_view.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}