# -*- coding: utf-8 -*-
{
    'name': "Labarindo Sale Order Modifier",



    'description': """
       This module changes numbering of Sale Order""",
    'author': "Hashmicro / TechUltra Solutions - Krutarth Patel",
    'website': "http://www.techultrasolutions.com/",

    'category': 'Sale',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['sale'],

    # always loaded
    'data': [
        'views/sale_order_modifier.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
    "installable": True,
    "auto_install": False,
    "application": True,
}


