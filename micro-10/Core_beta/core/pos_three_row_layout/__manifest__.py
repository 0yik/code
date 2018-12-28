# -*- coding: utf-8 -*-
{
    'name': "pdp_point_of_sale_layout",

   
    'description': """
        This module intends to change the layout for the Point of Sales
    """,
    'author': 'HashMicro / MP technolabs - Parikshit Vaghasiya',
    'website': 'www.hashmicro.com',

    'category': 'pos',
    'version': '0.1',

    'depends': ['base','point_of_sale','pos_promotion_program','pos_orders'],

    # always loaded
    'data': [
        'views/views.xml',
    ],
    # only loaded in demonstration mode
    'qweb':['static/src/xml/pos.xml'],
    'demo': [
    ],
}