# -*- coding: utf-8 -*-
{
    'name': "Forecasted Quantity Breakdown",

    'summary': """
        Show the Forecasted Incoming Quantity and Forecasted Outgoing Quantity at Product list view.""",

    'description': """
        Show the Forecasted Incoming Quantity and Forecasted Outgoing Quantity at Product list view.
    """,

    'author': "HashMicro/ Krupesh",
    'website': "https://www.hashmicro.com/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'stock',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'stock', ],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        # 'views/views.xml',
        # 'views/templates.xml',
        'views/product_view.xml',
        'views/stock_move_view.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo/demo.xml',
    ],
}
