# -*- coding: utf-8 -*-
{
    'name': "TM Product Sale",

    'description': """
        Product
    """,
    'author': 'HashMicro / Quy',
    'website': 'www.hashmicro.com',

    'category': 'sale,invoice',
    'version': '1.0',

    'depends': ['product_category','branch'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/product_sale.xml',
    ],
    # only loaded in demonstration mode
    'qweb': [],
    'demo': [
    ],
}