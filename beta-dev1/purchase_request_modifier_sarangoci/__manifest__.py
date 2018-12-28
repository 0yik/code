# -*- coding: utf-8 -*-
{
    'name': "purchase_request_modifier_sarangoci",

    'summary': """Add branch to purchase request""",

    'version' : '1.0',
    'category': 'purchase',
    'author': 'HashMicro / Viet',
    'description': """Add branch to purchase request
    """,
    'website': 'www.hashmicro.com',

    # any module necessary for this one to work correctly
    'depends': ['base','branch','purchase_request'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
}