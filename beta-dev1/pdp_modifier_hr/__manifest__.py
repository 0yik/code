# -*- coding: utf-8 -*-
{
    'name': "pdp_modifier_HR",

    

    'description': """
        modify fields
    """,

    'author': 'HashMicro / MP technolabs / Prakash',
    'website': 'www.hashmicro.com',


    'category': 'HR',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['hr','branch'],

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
}