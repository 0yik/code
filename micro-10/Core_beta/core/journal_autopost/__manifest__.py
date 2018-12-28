# -*- coding: utf-8 -*-
{
    'name': "Journal Autopost",

    'summary': """
        Module will helps to Autopost journal entry at the creation time""",

    'description': """
    """,

    'author': "HashMicro / Mptechnolabs - Parikshit Vaghasiya/Naresh",
    'website': "www.hashmicro.com",
    'category': 'Uncategorized',
    'version': '1.0',

    # any module necessary for this one to work correctly
    'depends': [
        'base','sale','account'
    ],

    # always loaded
    'data': [
        'views/res_acc_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}