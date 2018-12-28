# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': "pos_cost_price",

    'summary': """
        Display Cost Price for each product in the POS.""",

    'description': """
Display Cost Price for each product in the POS.
    """,

    'website': "http://www.mptechnolabs.com/",
    'category': 'Point Of Sale',
    'version': '1.0',
    'depends': ['point_of_sale'],
    'data': [
        'views/pos_cost_price.xml',
    ],
    'qweb': ['static/src/xml/pos.xml'],

}
