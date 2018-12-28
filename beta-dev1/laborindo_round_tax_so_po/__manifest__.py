# coding=utf-8
{
    'name': "Laborindo Round Tax SO PO",



    'description': """
       This module is used to make rounding for Sales Order and Purchase Order total amounts including Tax amount""",

    'author': "Hashmicro / TechUltera Solution - Krutarth Patel",
    'website': "www.techultrasolutions.com/",

    'category': '',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['sale', 'purchase'],

    # always loaded
    'data': [
        # 'views/purchase_order_modification.xml',
        # 'wizard/purchase_landed_cost.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo/demo.xml',
    ],
    "installable": True,
    "auto_install": False,
    "application": True,
}


