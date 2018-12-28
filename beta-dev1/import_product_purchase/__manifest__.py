# -*- coding: utf-8 -*-
{
    'name' : 'Import Product Purchase',
    'version' : '1.0',
    'category': 'Purchase',
    'author': 'HashMicro / MP technolabs(Chankya)',
    'description': """
        This module will import products in purchase order line.
    """,
    'website': 'www.hashmicro.com',
    'depends' : ['purchase'],
    'data': [
        'wizard/order_line_import_wizard.xml',
        'views/purchase_order_view.xml',
    ],
    'demo': [
    ],
    'qweb': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}
