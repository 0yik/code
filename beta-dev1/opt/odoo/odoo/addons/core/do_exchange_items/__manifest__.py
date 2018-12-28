# -*- coding: utf-8 -*-
{
    'name': 'Do Exchange Items',
    'summary': 'Allow users to exchange for items in DO and auto create the stock moves',
    'description': 'Allow users to exchange for items in DO and auto create the stock moves',
    'version': '1.0',
    'category': '',
    'author': 'Hashmicro/Janbaz Aga',
    'website': 'www.hashmicro.com',
    'depends': ['stock'],
    'data': [
        'wizard/do_exchange.xml',
        'views/stock_picking.xml',
    ],
    'application': True,
}
