# -*- coding: utf-8 -*-
{
    'name': "analytic_account_selectable",

    'description': """
        a. Add field in form view
            a.i. Selectable – checkbox 
            a.ii. When this field is checked, this record will show in the dropdowns
            a.iii. When this field is NOT checked, this record will NOT show in the dropdowns
    """,

    'author': "HashMicro / Vu",
    'website': "http://www.hashmicro.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '1.0',

    # any module necessary for this one to work correctly
    'depends': ['base', 'analytic'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/account_analytic_view.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}