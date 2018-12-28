# -*- coding: utf-8 -*-
{
    'name': "delivery_orders_kds",

    'summary': """
        Register Payment Customer Invoice from POS payment Screen""",

    'description': """
        Register Payment Customer Invoice from POS payment Screen
    """,

    'author': "HashMicro/ Sang",
    'website': "http://www.hashmicro.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'stock', 'sale', 'point_of_sale', 'pos_restaurant', 'pos_to_sales_order', 'pizzahut_modifier_startscreen', 'hr'],

    # always loaded
    'data': [
        'views/pos_delivery_templates.xml',
        'views/stock_picking_views.xml',
        'data/data.xml',
    ],
    # only loaded in demonstration mode
    'qweb': ['static/src/xml/*.xml'],
}