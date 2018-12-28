# -*- coding: utf-8 -*-
{
    'name': "TM Point of sale Receipt",

   
    'description': """
        This module Extend POS receipt.
    """,
    'author': 'HashMicro / MP technolabs - Parikshit Vaghasiya',
    'website': 'www.hashmicro.com',

    'category': 'pos',
    'version': '0.1',

    'depends': ['base','point_of_sale','sale','purchase','credit_debit_note','pos_home_delivery'],

    # always loaded
    'data': [
        'data/TM_sequence_data.xml',
        'views/views.xml',
    ],
    # only loaded in demonstration mode
    'qweb':['static/src/xml/pos.xml'],
    'demo': [
    ],
}