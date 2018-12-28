# coding=utf-8
{
    'name': "Purchase Landed Cost Modifier",



    'description': """
       This module adds landed cost to purchase order""",

    'author': "Hashmicro / TechUltera Solution - Krutarth Patel",
    'website': "www.techultrasolutions.com/",

    'category': 'Purchase',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['purchase', 'stock_landed_costs'],

    # always loaded
    'data': [
        'views/purchase_order_modification.xml',
        'wizard/purchase_landed_cost.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo/demo.xml',
    ],
    "installable": True,
    "auto_install": False,
    "application": True,
}


