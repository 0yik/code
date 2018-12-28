# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


{
    'name': 'POS Startscreen',
    'version': '1.0',
    'category': 'POS',
    'author': 'Hashmicro/Sang',
    'website': 'http://www.hashmicro.com/',
    'description': """
    Create start popup for pos startscreen
""",
    'depends': ['point_of_sale', 'pos_restaurant', 'pos_restaurant_kitchen','pos_to_sales_order'],
    'data': [
        'views/template.xml',
    ],
    'qweb': ['static/src/xml/start_screen.xml'],
    'demo': [
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
