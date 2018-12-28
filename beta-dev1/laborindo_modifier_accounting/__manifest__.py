# -*- coding: utf-8 -*-
{
    'name': "Labarindo Account Modifier",



    'description': """
       This module adds menu to Accounting for account type""",
    'author': "Hashmicro / TechUltra Solutions - Krutarth Patel",
    'website': "http://www.techultrasolutions.com/",

    'category': 'Account',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['account'],

    # always loaded
    'data': [
        'views/account_modifier.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
    "installable": True,
    "auto_install": False,
    "application": True,
}


