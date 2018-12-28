# -*- coding: utf-8 -*-
{
    'name': "hm Visitor",

    'summary': """
        Module will helps to Create visitor view""",

    'description': """
    """,

    'author': "HashMicro / Mptechnolabs - Parikshit Vaghasiya",
    'website': "www.hashmicro.com",
    'category': 'Uncategorized',
    'version': '1.0',

    # any module necessary for this one to work correctly
    'depends': [
        'base','sale'
    ],

    # always loaded
    'data': [
        'views/res_visitor_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}