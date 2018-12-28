# -*- coding: utf-8 -*-
{
    'name': "pos_delivery_address",

    'summary': """
        All delivery address of customer in POS .""",

    'description': """
        All delivery address of customer in POS .
    """,

    'author': "HashMicro/MP Technolabs/Purvi",
    'website': "http://www.hashmicro.com",

    'category': 'Uncategorized',
    'version': '0.1',

    'depends': ['point_of_sale', 'multiple_customer_delivery_address'],

    'data': ['views/pos_templates.xml',
    'views/pos_order_view.xml'],
    'qweb': ['static/src/xml/*.xml'],
}
