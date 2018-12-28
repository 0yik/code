# -*- coding: utf-8 -*-
{
    'name': "TM Pos to so Extend",

   
    'description': """
        This module intends to apply promotion and discount when create sales order.
    """,
    'author': 'HashMicro / MP technolabs - Parikshit Vaghasiya',
    'website': 'www.hashmicro.com',

    'category': 'pos',
    'version': '0.1',

    'depends': ['base','point_of_sale','pos_to_sales_order','pos_promotion'],

    # always loaded
    'data': [
        'views/views.xml',
    ],
    # only loaded in demonstration mode
    'qweb':['static/src/xml/pos.xml'],
    'demo': [
    ],
}