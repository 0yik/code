# -*- coding: utf-8 -*-
{
    'name': "stock_card_report",

    'summary': """
        stock card report""",

    'description': """
        stock card report
    """,

    'author': "HashMicro / MPTechnolabs - Dhaval",
    'website': "https://www.hashmicro.com",

    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['stock', 'branch'],

    # always loaded
    'data': [
        'data/stock_card_report_data.xml',
        'views/stock_card_report_views.xml',
        'views/templates.xml',
        'views/report_stock_card_template.xml'
    ],
    'qweb': [
        'static/src/xml/pivot.xml',
    ],
    'installable': True,
    'auto_install': False
}