# -*- coding: utf-8 -*-
{
    'name': "hm_realestate_owners",

    'summary': """
        hm_realestate_owners""",

    'description': """
    """,

    'author': "HashMicro / Mptechnolabs - Bipin Prajapati",
    'website': "www.hashmicro.com",
    'category': 'Uncategorized',
    'version': '1.0',

    # any module necessary for this one to work correctly
    'depends': [
        'sale','stable_account_analytic_analysis','hm_realestate'
    ],

    # always loaded
    'data': [
        'views/sale_view.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
    'installable': True,
    'auto_install': False,
}