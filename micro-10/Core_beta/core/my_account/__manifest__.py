# -*- coding: utf-8 -*-
{
    'name': "My Account",

    'summary': """
        My accouting""",

    'description': """
        My accouting
    """,

    'author': "HashMicro / Vu",
    'website': "http://www.hashmicro.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Account',
    'version': '1.0',

    # any module necessary for this one to work correctly
    'depends': [
        'account',
    ],

    # always loaded
    'data': [
        'data/functions.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
    'auto_install': True,
}