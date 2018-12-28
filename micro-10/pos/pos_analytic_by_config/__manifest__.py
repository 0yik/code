# -*- coding: utf-8 -*-
{
    'name': "POS Analytic Config",

    'summary': """
        Use analytic account defined on
                  POS configuration for POS orders""",

    'description': """
        Use analytic account defined on
                  POS configuration for POS orders
    """,

    'author': "HashMicro / Vu",
    'website': "http://www.hashmicro.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Point Of Sale, Accounting',
    'version': '1.0',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'point_of_sale',
        'account'
    ],

    # always loaded
    'data': [
        'views/pos_config_view.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}
