# -*- coding: utf-8 -*-
{
    'name': 'Warehouse Modifier Shop',
    'version': '1.0',
    'category': 'Inventory',
    'sequence': 17,
    'summary': 'setup for creating branch and warehouse based on checkbox.',
    'description': "This module includes setup for creating branch and warehouse based on enable checkbox.",
    'website': 'http://www.hashmicro.com/',
    'author': 'Hashmicro/Kannan',
    'depends': ['stock','branch','pdp_modifier_branch'],
    'data': [
        'views/branch_view.xml',
        'views/stock_view.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
