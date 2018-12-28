# -*- coding: utf-8 -*-
{
    'name': "POS Multiple Category",
    'description': """
        This module add POS multiple category.
    """,
    'author': 'HashMicro / Justcodify',
    'website': 'www.hashmicro.com',
    'category': 'POS',
    'version': '1.0',
    'depends': ['point_of_sale'],
    'data': [
        'views/pos_multiple_category_view.xml',
        'views/multiple_pos_categ.xml'
    ],
    'qweb': [],
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}