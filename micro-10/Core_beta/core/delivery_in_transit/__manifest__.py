
# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Delivery In Transit',
    'version': '10.0',
    'author': 'HashMicro/Naresh',
    'category': 'Delivery In Transit',
    'sequence': 100,
    'summary': 'Transit state added in Delivery order and further operation carried',
    'description': """
Delivery In Transit
====================
Delivery In Transit

    """,
    'website': 'www.hashmicro.com',
    'images': [
       
    ],
    'depends': ['stock'],
    'data': [
        'view/delivery_transit_view.xml',
#         'data/stock_data.xml',
        'wizard/transit_immediate_transfer_view.xml'
    ],
    'demo': [
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'qweb': [],
}
