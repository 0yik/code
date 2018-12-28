# -*- coding: utf-8 -*-
{
    'name': "Bank Transaction IN and Out",

    'summary': """
        Bank Transaction Extended module""",

    'description': """
        Bank Transaction
    """,

    'author': "HashMicro / MP Technolabs - Parikshit Vaghasiya",
    'website': "http://www.hashmicro.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Accounting',
    'version': '1.0',

    # any module nece0ssary for this one to work correctly
    'depends': ['account'],

    # always loaded
    'data': [
        'views/matahari_bank_account_view.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}