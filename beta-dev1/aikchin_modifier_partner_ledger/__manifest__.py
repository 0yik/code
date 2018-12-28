# -*- coding: utf-8 -*-
{
    'name': "aikchin_modifier_partner_ledger",

    'summary': """
        Modify the partner ledger report""",

    'description': """
        Modify the partner ledger report
    """,

    'author': "Hashmicro / Luc",
    'website': "http://www.hashmicro.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','account','sg_account_standardisation', 'branch'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/partner_ledger_report_view.xml',
        'views/partner_ledger_balance_view.xml',
    ],
}