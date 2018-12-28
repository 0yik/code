# -*- coding: utf-8 -*-
{
    'name': 'POS Other Branch',
    'version': '1.0',
    'category': 'Point Of Sale',
    'author': 'HashMicro / Saravanakumar',
    'summary': 'POS Switching Warehouse',
    'description': "This module provides option to choose different POS to deduct the stock in selected POS wharehouse",
    'website': 'www.hashmicro.com',
    'depends': ['pos_restaurant'],
    'data': [
        'views/define.xml',
    ],
    'qweb': [
        'static/src/xml/*.xml'
    ],
    'installable': True,
    'application': True,
}
