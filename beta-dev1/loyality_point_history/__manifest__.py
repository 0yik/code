# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


{
    'name': 'Loyalty Point History',
    'version': '1.0',
    'category': 'Point of Sale',
    'sequence': 6,
    'summary': '',
    'description': """

=======================

""",
    'depends': ['point_of_sale', 'pos_orders', 'pos_order_return', 'pos_loyalty'],
    'data': [
        'views/template.xml',
    ],
    'qweb': ['static/src/xml/loyality.xml'],
    'demo': [
    ],
    'installable': True,
    'auto_install': False,
    'license': 'OEEL-1',
}
