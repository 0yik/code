# -*- coding: utf-8 -*-
{
    'name': "beumer_modifier_fields",

    'description': """
        beumer modifier fields
    """,

    'author': "HashMicro/Vu",
    'website': "http://www.hashmicro.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '1.0',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'product',
        'purchase',
        'hr',
        'account',
        'hr_expense',
        'multi_category_analytic_account',
        'expense_masking',
        'stable_account_analytic_analysis',
        'analytic',
        'analytic_approving_extension',
    ],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/product_view.xml',
        'views/res_partner_view.xml',
        'views/hr_employee_view.xml',
        'views/remark_view.xml',
        'views/hr_expense_line_view.xml',
        'views/modifier_project_manager.xml',
        'views/hr_employee_modifier.xml',
    ],
    # only loaded in demonstration mode
    'demo': [

    ],
}