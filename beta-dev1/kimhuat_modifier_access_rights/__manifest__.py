# -*- coding: utf-8 -*-
{
    'name': "kimhuat_modifier_access_rights",

    'summary': """
        """,

    'description': """
    """,

    'author': "HashMicro / Hoang",
    'website': "http://www.hashmicro.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'purchase',
        'stock',
        'purchase_request',
        'sale',
        'payment',
        'account',
        'hr',
        'hr_timesheet_sheet',
        'sale_expense',
        'hr_expense',
        'hr_holidays',
        'product',
        'analytic',
    ],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/kimhuat_security.xml',
        'security/ir.model.access.csv',
        'views/modifier_kimhuat_view.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo/demo.xml',
    ],
}