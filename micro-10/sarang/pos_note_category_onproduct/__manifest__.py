# -*- coding: utf-8 -*-
{
    'name': "pos_note_category_onproduct",

    'summary': """
        pos_note_category_onproduct""",

    'description': """
        pos_note_category_onproduct
    """,

    'author': "JustCodify",

    # for the full list
    'category': 'POS',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['pos_note_category'],
    'qweb': [
        'static/src/xml/pos_orderline.xml'
    ],
    # always loaded
    'data': [
        'views/template.xml',
        'views/product_note_view.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}