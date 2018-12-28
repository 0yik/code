# -*- coding: utf-8 -*-
{
    'name': "pos_bus_add_queue",

    'summary': """
        Use queue to push messages, avoid loading """,

    'description': """
        Using queue to push message
    """,

    'author': "HashMicro/ Sang",
    'website': "http://www.hashmicro.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['pos_bus'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
}