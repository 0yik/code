# -*- coding: utf-8 -*-
{
    'name': "POS Sarang receipt Layout",

   
    'description': """
        This module intends to change the layout for the Point of Sales Receipt
    """,
    'author': 'HashMicro / MP technolabs - Purvi Pandya',
    'website': 'www.hashmicro.com',

    'category': 'pos',
    'version': '0.1',

    'depends': ['base','branch','pos_price_charges_calculation'],
    'data': [
        'views/templates.xml',
    ],
    'qweb':['static/src/xml/pos.xml','static/src/xml/print_receipt_layout.xml'],
    'demo': [
    ],
}