# -*- coding: utf-8 -*-
{
    'name': "laborindo_modifier_inventory_valuation",
   
    'description': """
       Added New field in Inventory  Valuation
    """,
    'author': 'HashMicro / MP technolabs / Prakash',
    'website': 'www.hashmicro.com',

    'category': 'Stock',
    'version': '1.0',

    # any module necessary for this one to work correctly
    'depends': ['stock','laborindo_modifier_product','inventory_valuation_sales_price'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}