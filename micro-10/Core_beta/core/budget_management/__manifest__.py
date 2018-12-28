# -*- coding: utf-8 -*-
{
    'name': 'Budget Management',
    'category': 'Sale',
    'summary': 'Setting approval levels for budget setting and budget changes',
    'description': 'Setting approval levels for budget setting and budget changes',
    'sequence': 1,
    'author': 'HashMicro / Abulkasim Kazi / Saravanakumar',
    'website': 'www.hashmicro.com',
    'version': '1.0',
    'depends': ['account_budget','account_accountant'],
    'data': [
        'security/ir.model.access.csv',
        'views/readonly_bypass.xml',
        'views/budget_view.xml',
        'views/budget_change_request.xml',
        'views/budget_reserve_request.xml',
        'views/budget_allocation_request.xml',
        'views/analytic_account_view.xml',
    ],
    'installable': True,
    'application': True,
}
