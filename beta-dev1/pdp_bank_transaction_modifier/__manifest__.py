# -*- coding: utf-8 -*-
{
    'name': "pdp_bank_transaction_modifier",

    'summary': """
        PDP Bank Transaction""",

    'description': """
        Bank Transaction
    """,

    'author': "HashMicro / Hoang",
    'website': "http://www.hashmicro.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Accounting',
    'version': '1.0',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'account',
        'branch',
        'bank_transaction'
    ],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/bank_transaction_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}