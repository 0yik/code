# -*- coding: utf-8 -*-
{
    'name': 'TM_pos_sales_credit',
    'version': '1.0',
    'category': 'Point of sale',
    'author': 'HashMicro / Viet',
    'description': """Tomadju pos customer sale credit 
    """,
    'website': 'www.hashmicro.com',
    'depends': ['base', 'point_of_sale', 'partner_credit_limit','TM_pos_to_so_extended'],
    'data': [
        'views/views.xml',
    ],
    'demo': [
    ],
    'qweb': [
        'static/src/xml/*.xml',
    ],
}