# -*- coding: utf-8 -*-
{
    'name': "Lookup Values Master",



    'description': """
       This module adds menu to Settings to store master values""",
    'author': "Hashmicro / TechUltra Solutions - Krutarth Patel",
    'website': "http://www.techultrasolutions.com/",

    'category': '',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base'],

    # always loaded
    'data': [
            'views/lookup_values_view.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
    "installable": True,
    "auto_install": False,
    "application": True,
}


