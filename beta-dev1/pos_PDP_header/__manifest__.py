# -*- coding: utf-8 -*-
{
    'name': "pos_PDP_header",


    'description': """
        This module intends to change the color of header of Point of Sales view and the logo of the company in Point of Sales View
    """,

    'author': 'HashMicro / MP technolabs / Prakash',
    'website': 'www.hashmicro.com',

    'category': 'pos',
    'version': '0.2',

    'depends': ['base','point_of_sale'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
    ],
    'qweb':['static/src/xml/logochange.xml'],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}