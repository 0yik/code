# -*- coding: utf-8 -*-
{
    'name': "pdp_modifier_branch",


    'description': """
        Modify the fields
    """,

    'author': 'HashMicro / MP technolabs / Prakash',
    'website': 'www.hashmicro.com',

    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['branch','hr'],

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
