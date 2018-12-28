# -*- coding: utf-8 -*-
{
    'name': "pos_modifier_tax",

    'description': """
        This module intends to hide the percentage of price tax included from tax computation in accounting
    """,
    'author': 'HashMicro / MP technolabs / Prakash',
    'website': 'www.hashmicro.com',

    'category': 'Account',
    'version': '0.1',
    

    # any module necessary for this one to work correctly
    'depends': ['base','account'],

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