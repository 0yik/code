# -*- coding: utf-8 -*-
{
    'name': 'POS Last Sold Price',
    'version': '0.1',
    'category': 'Uncategorized',
    'summary': 'This module allow Salesperson can view last sold price depends on Product and Customer',
    'description': """
    Last Updated 11 January 2018
This module allow Salesperson can view last sold price depends on Product and Customer.
""",
    'author': "hashmicro/ Duy",
    'website': "http://www.hashmicro.com",
    'depends': ['base','sale','pos_location_qty'],
    "data": [
        'views/pos_last_sold_price.xml',
    ],
    'qweb': [
            'static/src/xml/pos.xml'
    ],
}

