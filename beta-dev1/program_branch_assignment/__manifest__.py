# -*- coding: utf-8 -*-
{
    'name': "Program Branch Assignment",


    'description': """
        Branch field to Promotion program.
    """,

    'author': 'HashMicro / GYB IT SOLUTIONS / Anand',
    'website': 'www.hashmicro.com',

    'category': 'pos promotion',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['branch','pos_base','pos_promotion'],

    # always loaded
    'data': [
        'views/program_branch.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
    'application': True,
}
