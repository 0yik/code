# -*- coding: utf-8 -*-
{
    'name': "low_stock_notification_runrate",

    'description': """
        - Add option Run Rate for Low Stock Notification
    """,

    'author': "HashMicro/Vu",
    'website': "http://www.hashmicro.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '1.0',

    # any module necessary for this one to work correctly
    'depends': ['base', 'stock', 'product', 'low_stock_notification'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/low_stock_notification_runrate_view.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}