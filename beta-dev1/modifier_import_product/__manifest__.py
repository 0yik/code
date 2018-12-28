# -*- coding: utf-8 -*-
{
    'name' : 'Modifier Import Product',
    'version' : '1.0',
    'category': 'Sales',
    'author': 'HashMicro / MP technolabs(Chankya)',
    'description': """
        This module will import products in sale order line.
    """,
    'website': 'www.hashmicro.com',
    'depends' : ['pdp_modifier_sales'],
    'data': [
        'wizard/order_line_import_wizard.xml',
        'views/sale_order_view.xml',
    ],
    'demo': [
    ],
    'qweb': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}
