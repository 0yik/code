# -*- coding: utf-8 -*-
{
    'name': "manufacturing_plan_contract",

    'summary': """
        Manufacturing Plan Contract""",

    'description': """
        Manufacturing Plan Contract
    """,

    'author': "HashMicro / Duy",
    'website': "http://www.hashmicro.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'version': '1.0',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'mrp',
        'stock',
        'account',
        'manufacturing_plan',
        'sale',
        'stable_account_analytic_analysis'
    ],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/account_analysis_account_view.xml',
    ],
    'demo': [
    ],
}