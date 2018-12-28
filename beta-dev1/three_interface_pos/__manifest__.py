# -*- coding: utf-8 -*-
{
    'name': "Pos Screen in 3 Parts",

   
    'description': """
        This module intends to change the layout for the Point of Sales in 3 parts
    """,
    'author': 'HashMicro / MP technolabs - Purvi',
    'website': 'www.hashmicro.com',

    'category': 'pos',
    'version': '0.1',

    'depends': ['base','pos_restaurant_kitchen'],


    # always loaded
    'data': [
        'views/views.xml',
    ],
    # only loaded in demonstration mode
    'qweb':['static/src/xml/pos.xml'],
    'demo': [
        'demo/demo.xml',
    ],
}