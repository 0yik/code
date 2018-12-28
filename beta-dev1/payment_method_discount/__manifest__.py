# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Payment method discount',
    'version': '1.0',
    'category': 'POS',
    'author': 'Hashmicro/MP Technolabs / Vatsal',
    'website': 'http://www.hashmicro.com/',
    'description': """

=======================

""",
    'depends': ['point_of_sale','pos_restaurant','account'],
    'data': [
        'data/payment_method_discount_data.xml',
        'views/template.xml',
        'views/account_journal_view.xml',

    ],
    'qweb': [
            'static/src/xml/payment_method_discount.xml',
             ],

    'demo': [
    ],

    'installable': True,
    'auto_install': False,
    'application': True,
}
