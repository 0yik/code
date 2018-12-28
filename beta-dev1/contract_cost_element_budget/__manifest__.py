# -*- coding: utf-8 -*-
{
    'name': "contract_cost_element_budget",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "HashMicro / Vu",
    'website': "http://www.hashmicro.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '1.0',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'sale',
        'purchase',
        'account',
        'analytic',
        'cost_element',
        'stable_account_analytic_analysis',
        'multiple_rfq_pr',
        'analytic_approving_extension',
    ],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'wizard/account_analytic_budget_change_views.xml',
        'views/purchase_order.xml',
        'views/sale_order.xml',
        'views/account_invoice.xml',
        'views/analytic_account.xml',
        'views/purchase_request.xml',

    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}
