# -*- coding: utf-8 -*-

{
    'name': 'Inventory Pivot Report ',
    'version': '1.0',
    'category': 'Inventory',
    'summary': 'Creating New Pivot Report for Inventory Stock',
    'description': """
    This module generates Pivot Report for Inventory Stock 
    """,
    'author': 'HashMicro / GBS',
    'website': 'www.hashmicro.com',
    'depends': [
        'sales_field_city'
    ],
    'data': [
        'views/stock_quant_view.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}