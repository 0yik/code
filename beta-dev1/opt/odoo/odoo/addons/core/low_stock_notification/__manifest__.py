# -*- coding: utf-8 -*-
{
    'name': "low_stock_notification",

    'description': """
        - Have a scheduler that checks once a day (preferably on 6am SGT), if any product on any location in that tree view has hit <= quantity
                 If yes, send the template email to the “Email to”
    """,

    'author': "HashMicro/Vu",
    'website': "http://www.hashmicro.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '1.0',

    # any module necessary for this one to work correctly
    'depends': ['base', 'stock', 'product'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/low_stock_notification_view.xml',
        'data/ir_cron.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}