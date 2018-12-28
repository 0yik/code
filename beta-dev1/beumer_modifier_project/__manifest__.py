# -*- coding: utf-8 -*-
{
    'name': "beumer_modifier_project",

    'description': """
        Changing Contract into Project with necessary fields
    """,

    'author': "HashMicro/Vu",
    'website': "http://www.hashmicro.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '1.0',

    # any module necessary for this one to work correctly
    'depends': ['base', 'analytic', 'sales_team', 'stable_account_analytic_analysis'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/account_analytic_account_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}