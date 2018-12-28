# -*- coding: utf-8 -*-
{
    'name': "pos_item_number",

    'summary': """
        Display sequence in selected products in POS .""",

    'description': """
        Display sequence in selected products in POS .
    """,

    'author': "HashMicro/MP Technolabs/Purvi",
    'website': "http://www.hashmicro.com",

    'category': 'Uncategorized',
    'version': '0.1',

    'depends': ['point_of_sale'],

    'data': ['views/pos_templates.xml'],
    'qweb': ['static/src/xml/pos.xml'],
    'demo': [
    ],
}