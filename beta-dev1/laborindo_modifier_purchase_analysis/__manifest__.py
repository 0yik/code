# coding=utf-8
# -*- coding: utf-8 -*-
{
    'name': "Laborindo Purchase Analysis",
    'description': """This module adds modifications to Pivot view of Purchase report

       """,
    'author': "Hashmicro / Krutarth Patel",
    'website': "",
    'category': 'Purchase',
    'version': '0.1',
    # any module necessary for this one to work correctly
    'depends': ['laborindo_product_brand_list', 'laborindo_modifier_product'],
    # always loaded
    'data': [
        'views/purchase_report_view.xml',
    ],
    # only loaded in demonstration mode
    'demo': [],
    "installable": True,
    "auto_install": False,
    "application": True,
}


