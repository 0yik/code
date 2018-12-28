# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Pizzahut Takeaway Order',
    'version': '1.0',
    'category': 'POS',
    'author': 'Hashmicro/MP Technolabs / Vatsal',
    'website': 'http://www.hashmicro.com/',
    'description': """

=======================

""",
    'depends': ['base','pizzahut_modifier_startscreen','pos_restaurant','pos_to_sales_order','seat_number_table'],
    'data': [
        'views/template.xml',
    ],
    'qweb': ['static/src/xml/take_away_order.xml',
            'static/src/xml/hide_create_sale_order_button.xml',
            'static/src/xml/hide_seat_number_button.xml',
             ],

    'demo': [
    ],

    'installable': True,
    'auto_install': False,
    'application': True,
}
