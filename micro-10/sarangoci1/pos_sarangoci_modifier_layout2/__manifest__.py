# -*- coding: utf-8 -*-
{
    'name': "POS Sarang Priority buttons hide",

   
    'description': """
        This module intends to hide the buttons in POS 
    """,
    'author': 'HashMicro / MP technolabs - Parikshit Vaghasiya',
    'website': 'www.hashmicro.com',

    'category': 'pos',
    'version': '0.1',

    'depends': ['base','pos_restaurant_kitchen', 'pos_sarang_oci_layout'],
    'data': [
        'views/templates.xml',
    ],
    'qweb':['static/src/xml/pos.xml'],
    'demo': [
    ],
}