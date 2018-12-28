# -*- coding: utf-8 -*-
{
    'name': "manufacturing_plan_timesheet",

    'summary': """
        Manufacturing Plan Timesheet""",

    'description': """
        Manufacturing Plan Timesheet
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
        'manufacturing_plan',
        'manufacturing_plan_contract',
        'stable_account_analytic_analysis'
    ],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/manu_facturing_order_view.xml',
    ],
    'demo': [
    ],
}