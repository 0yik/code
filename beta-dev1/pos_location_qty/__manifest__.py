# -*- coding: utf-8 -*-
{
    'name': 'POS Location Quantity',
    'version': '0.1',
    'category': 'Uncategorized',
    'summary': 'This module allow user to show product quantity from location',
    'description': """
    Last Updated 11 January 2018
This module allow user to check product quantity in different location.
""",
    'author': "hashmicro/ Duy",
    'website': "http://www.hashmicro.com",
    'depends': ['base','purchase'],
    "data": [
        'views/pos_warehouse_qty.xml',
    ],
    'qweb': [
            'static/src/xml/pos.xml'
    ],
}

