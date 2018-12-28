# -*- coding: utf-8 -*-
{
    'name': "hm realestate",

    'summary': """
        Module will helps to customise product form view and add property view""",

    'description': """
    """,

    'author': "HashMicro / Mptechnolabs - Parikshit Vaghasiya",
    'website': "www.hashmicro.com",
    'category': 'Uncategorized',
    'version': '1.0',

    # any module necessary for this one to work correctly
    'depends': [
        'base','sale','stable_account_analytic_analysis'
    ],

    # always loaded
    'data': [
        'views/res_product_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}