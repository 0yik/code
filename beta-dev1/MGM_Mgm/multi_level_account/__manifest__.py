# -*- coding: utf-8 -*-
{
    'name': "Multi Level Account",

    'summary': """
        Generate Multi Level Analytic Account""",

    'description': """
        Generate Multi Level Analytic Account
    """,

    'author': "HashMicro/ Krupesh",
    'website': "http://www.hashmicro.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Account',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'account',],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/analytic_account_view.xml',
        'views/multi_level_aa_view.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        #'demo/demo.xml',
    ],
}
