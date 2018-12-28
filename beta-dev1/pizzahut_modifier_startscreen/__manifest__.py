# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


{
    'name': 'Pizzahut Modifier Startscreen',
    'version': '1.0',
    'category': 'POS',
    'author': 'Hashmicro/GYB IT SOLUTIONS-Anand',
    'website': 'http://www.hashmicro.com/',
    'description': """

=======================

""",
    'depends': ['point_of_sale', 'pos_restaurant', 'pos_restaurant_kitchen','pos_to_sales_order'],
    'data': [
        'views/template.xml',
    ],
    'qweb': ['static/src/xml/pizzahut_mod_screen.xml'],
    'demo': [
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
