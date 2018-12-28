# -*- coding: utf-8 -*-
{
    'name': "budget_actual_report",

    'summary': """
        a. In Measure, add “Budget”
        b. Budget data to get from the Budget set in the Analytic Accounts""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Hashmicro /Luc",
    'website': "http://www.hashmicro.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','analytic','account_budget'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/account_analytic_line_pivot.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}