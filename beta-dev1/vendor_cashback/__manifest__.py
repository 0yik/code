# -*- coding: utf-8 -*-
{
    'name': "Telering Vendor Cashback",
    'description': """
        Telering Vendor Cashback
    """,
    'author': 'HashMicro / Abulkasim Kazi',
    'website': 'www.hashmicro.com',
    'category': 'sale, point_of_sale',
    'version': '1.0',
    'depends': ['sale', 'account_accountant', 'point_of_sale'],
    # always loaded
    'data': [
        'views/vendor_cashback.xml'
    ],
    'qweb': [],
    'demo': [],
}