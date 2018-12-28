# -*- coding: utf-8 -*-
{
    "name": "Discount On Entire Purchase Order",
    "author": "HashMicro/Vinay",
    "version": "10.0.1.0",
    "website": "www.hashmicro.com",
    "category": "Purchase Management",
    "depends": ["purchase"],
    "data": [
        "views/purchase_order_view.xml",
    ],
    'description':'''
    1.	Add field “Discount” after Untaxed Amount (before Taxes) for users to input any additional discounts
    2.	Total to take into account of the Additional Discount as well
     
    Key Points:
    1.	Search for existing module for odoo 10 first
    2.	If found similar can use it and create this module to modify that module
    3.	If no similar modules then create this module
    ''',
    'demo': [],
    "installable": True,
    "auto_install": False,
    "application": True,
}