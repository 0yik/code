# -*- coding: utf-8 -*-
{
    'name': "pos_sarang_oci_layout",

   
    'description': """
        This module intends to change the layout for the Point of Sales
    """,
    'author': 'HashMicro / MP technolabs / Prakash',
    'website': 'www.hashmicro.com',

    'category': 'pos',
    'version': '0.1',

    'depends': ['base','point_of_sale','pos_restaurant_kitchen','pos_bus_restaurant','pos_discount_popup','branch_sales_report','sarangoci_modifier_branch'],


    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'qweb':['static/src/xml/pos.xml'],
    'demo': [
        'demo/demo.xml',
    ],
}