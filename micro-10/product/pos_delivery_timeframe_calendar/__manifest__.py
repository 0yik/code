# -*- coding: utf-8 -*-
{
    'name': "Pos Delivery Timeframe Calendar",

    'summary': """
        Synchronize timeframe setting and POS  calendar based on parameter""",

    'description': """
        Synchronize timeframe setting and POS  calendar based on parameter
    """,

    'author': "HashMicro/Balram",
    'website': "http://www.hashmicro.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','point_of_sale', 'pos_delivery_timeframe_management'],

    # always loaded
    'data': [
        'views/views.xml',
    ],

    'qweb': [
        'static/xml/*.xml'
    ],
}