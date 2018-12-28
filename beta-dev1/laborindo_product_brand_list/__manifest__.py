# coding=utf-8
# -*- coding: utf-8 -*-
{
    'name': "Labarindo Sale Order Modifier",



    'description': """
       Adds Product brand, category and sub category configuration in Inventory module""",
    'author': "Hashmicro / TechUltra Solutions - Krutarth Patel",
    'website': "http://www.techultrasolutions.com/",

    'category': 'Sale',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['stock'],

    # always loaded
    'data': [
        'views/product_brand_list.xml',
        'data/data.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
    "installable": True,
    "auto_install": False,
    "application": True,
}


