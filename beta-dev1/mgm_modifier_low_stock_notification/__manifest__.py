# -*- coding: utf-8 -*-
{
    'name': "mgm_modifier_low_stock_notification",

    'summary': """
        To add new column in products table own by MGM""",

    'description': """
        To add new column in products table own by MGM
    """,

    'author': "Rajnish",
    'website': "http://www.linescripts.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Inventory',
    'version': '1.0',

    # any module necessary for this one to work correctly
    'depends': ['base','low_stock_notification'],

    # always loadedlow_stock_notification
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}