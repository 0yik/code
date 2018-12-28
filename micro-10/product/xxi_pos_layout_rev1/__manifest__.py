# -*- coding: utf-8 -*-
{
    'name': "XXI POS Layout 1",

    'description': """
        Change the layout and copy the template from currently running system.
    """,
    'author': 'HashMicro / Janbaz Aga',
    'website': 'www.hashmicro.com',

    'category': 'pos',
    'version': '0.1',

    'depends': ['base', 'pos_restaurant_kitchen'],

    # always loaded
    'data': [
        'views/views.xml',
        'views/pos_config.xml',
    ],
    # only loaded in demonstration mode
    'qweb': ['static/src/xml/pos.xml'],
    'demo': [
        # 'demo/demo.xml',
    ],
}