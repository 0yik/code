# -*- coding: utf-8 -*-
{
    'name': "Indonesia POS Payments",

   
    'description': """
        This module intends to change the layout Payment Screen
    """,
    'author': 'HashMicro / MP technolabs - Purvi / Saravanakumar',
    'website': 'www.hashmicro.com',

    'category': 'pos',
    'version': '0.1',

    'depends': ['base','point_of_sale'],


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