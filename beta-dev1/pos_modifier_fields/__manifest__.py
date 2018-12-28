# -*- coding: utf-8 -*-
{
    'name': "pos_modifier_fields",

    

    'description': """
        Make check box validation for what menu/fields will show in POS
    """,

    'author': 'HashMicro / MP technolabs / Prakash',
    'website': 'www.hashmicro.com',

    
    'category': 'pos',
    'version': '0.1',

    'depends': ['base','point_of_sale','pos_restaurant'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
    ],

    'qweb':['static/src/xml/pos.xml'],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}