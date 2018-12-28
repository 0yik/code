# -*- coding: utf-8 -*-
{
    'name': 'Inventory Valuation Sale Price',
    'version': '1.0',
    'category': 'Inventory',
    'sequence': 18,
    'description': "Inventory Valuation based on sales Price for the product.",
    'website': 'http://www.hashmicro.com/',
    'author': 'Hashmicro/Mareeswaran',
    'depends': ['stock'],
    'data': [
        'views/stock_quant_view.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}