# -*- coding: utf-8 -*-
{
    'name': "pos_orderline_details_hide",

    'description': """
        This Module hide deatil orderline in Pos
        """,
   
    'author': 'HashMicro / MP technolabs - Prakash',
    'website': 'www.hashmicro.com',

    'category': 'pos',
    'version': '0.1',


    # any module necessary for this one to work correctly
    'depends': ['point_of_sale'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],

    'qweb':['static/src/xml/pos.xml'],
}