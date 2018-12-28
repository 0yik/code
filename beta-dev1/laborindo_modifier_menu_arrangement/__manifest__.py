# -*- coding: utf-8 -*-
{
    'name': "Labarindo Modifier Menu Arrangement",
    'description': """
       Arrange menu in Sale Order""",
    'author': "Hashmicro / Quy",
    'website': "www.hashmicro.com",

    'category': 'Sale',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['sale'],

    # always loaded
    'data': [
        'views/menu_arrange_so.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
    "installable": True,
    "auto_install": False,
    "application": False,
}


