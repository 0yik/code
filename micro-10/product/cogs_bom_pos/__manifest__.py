# -*- coding: utf-8 -*-
{
    'name': 'Cost In POS Order',
    'description': 'This module intends to have functionality to reduce bill of materials in inventory when importing POS process is done',
    'version': '1.0',
    'category': 'Point Of Sale',
    'author': 'HashMicro/ MPTechnolabs(Chankya)',
    'website': "http://www.hashmicro.com",
    'depends': [
        'point_of_sale', 'mrp'
    ],
    'data': [
             'views/pos_order_view.xml'
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
