# -*- coding: utf-8 -*-
{
    'name': "invoice_for_bank_pos",

    'summary': """
        Generate customer invoice based on payment method type = Bank through POS transaction""",

    'description': """
        generate customer invoice based on payment method type = Bank through POS transaction
    """,

    'author': "HashMicro/ Sang",
    'website': "http://www.hashmicro.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '1.0',

    # any module necessary for this one to work correctly
    'depends': ['base', 'account', 'point_of_sale'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/account_journal_views.xml',
        'views/customer_invoice_sync_views.xml',
        'data/data.xml',
    ],
}