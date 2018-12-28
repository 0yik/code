# -*- coding: utf-8 -*-

{
    'name': 'User Access Rights for Branch',
    'version': '1.0',
    'category': 'Inventory',
    'summary': 'Access Rights for Branch',
    'description': """
    This module generates Pivot Report for Inventory Stock 
    """,
    'author': 'HashMicro / GBS',
    'website': 'www.hashmicro.com',
    'depends': [
        'branch','stock'
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/brand_group_view.xml',
        'views/stock_quant_view.xml',

    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
