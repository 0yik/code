# -*- coding: utf-8 -*-
{
    'name': "cashier_function",

    'description': """
        Make one button to facilitate cashier.
    """,

    'author': "HashMicro / Hoang",
    'website': "http://www.hashmicro.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'POS',
    'version': '1.0',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'pos_layout'
    ],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
    ],
    'qweb': [
        'static/src/xml/pos_screen.xml',
    ],
}