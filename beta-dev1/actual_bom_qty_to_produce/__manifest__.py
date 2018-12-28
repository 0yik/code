# -*- coding: utf-8 -*-
{
    'name' : 'Actual Bom Quantity to produce',
    'version' : '1.0',
    'category': 'Inventory',
    'author': 'HashMicro / MP Technolabs - Purvi Pandya',
    'description': """Stock deduction and production for BOM.
    """,
    'website': 'www.hashmicro.com',
    'depends' : ['central_kitchen'],
    'data': [
        'wizard/product_produce_view.xml',
    ],

    'installable': True,
    'application': True,
    'auto_install': False,
}
