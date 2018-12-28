# -*- coding: utf-8 -*-
{
    'name': "Petty Cash",

    'summary': """
        Automated management of petty cash funds""",

    'description': """
    """,

    'author': "Hashmicro / Viet",
    'website': "http://www.hashmicro.com/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Accounting & Finance',
    'version': '1.0',

    # any module necessary for this one to work correctly
    'depends': [
        'account',
        'account_voucher',
        'product',
    ],

    # always loaded
    'data': [
        'security/petty_cash.xml',
        'security/ir.model.access.csv',
        'wizard/change_fund_view.xml',
        'wizard/close_fund_view.xml',
        'wizard/create_fund_view.xml',
        'wizard/issue_voucher_view.xml',
        'wizard/reconcile_view.xml',
        'wizard/reopen_view.xml',
        'views/petty_cash_view.xml',
    ],
}