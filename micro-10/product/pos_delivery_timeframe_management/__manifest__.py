# -*- coding: utf-8 -*-
{
    'name': "Pos Delivery Timeframe Management",

    'summary': """
        Creating setting and new menus for time frame  """,

    'description': """
        Creating setting and new menus for time frame  
    """,

    'author': "HashMicro/Balram",
    'website': "http://www.hashmicro.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','point_of_sale', 'delivery'],

    # always loaded
    'data': [
        'security/security.xml',
        'views/views.xml',
        'views/time_frame.xml',
        'views/pos_config.xml',
        #'data/data.xml',
    ],

    'qweb': [
        'static/xml/*.xml'
    ],
}
