# coding=utf-8
# -*- coding: utf-8 -*-
{
    'name': "Laborindo Sales Analysis",
    'description': """

       """,
    'author': "Hashmicro / Abulkasim Kazi",
    'website': "",
    'category': 'Sale',
    'version': '0.1',
    # any module necessary for this one to work correctly
    'depends': ['laborindo_product_brand_list', 'laborindo_modifier_product'],
    # always loaded
    'data': [
        'views/sale_report_view.xml',
    ],
    # only loaded in demonstration mode
    'demo': [],
    "installable": True,
    "auto_install": False,
    "application": True,
}


