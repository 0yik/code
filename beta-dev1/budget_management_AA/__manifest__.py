# -*- coding: utf-8 -*-
{
    'name': 'Budget Management AA',
    'version': '1.0',
    'category': 'Accounting',
    'sequence': 13,
    'summary': 'Modify the fields and create new budget AA module',
    'description': "Modify the fields and create new budget AA module",
    'website': 'www.mptechnolabs.com',
    'author': 'Bharat Chauhan',
    'depends': [
        'account', 'budget_management_extension', 'budget_management','stable_account_analytic_analysis',
        'account_analytic_parent','account_analytic_account_plan'
    ],
    'data': [
        'views/template.xml',
        'views/budget_ana_account.xml',
        'views/budget_aa_allocation.xml',
        'views/budget_aa_reserve.xml',
        'views/account_analytic_account.xml',
        'data/budget_setting.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
