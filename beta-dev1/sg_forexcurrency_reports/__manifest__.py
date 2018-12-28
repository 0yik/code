# -*- coding: utf-8 -*-

{
    'name': 'Account Foreign Currency Transactions',
    'version': '1.0',
    'category': 'Account',
    'author': 'HashMicro Purvi',
    'website': 'www.hashmicro.com',
    'summary': 'Report for foreign currency',
    'description': """

    """,
    'depends': ['base', 'web', 'account'],
    'data': [
    'views/account_view.xml',
    'wizard/account_report_transaction_view.xml',
    # 'views/account.xml',
    ],
    'qweb': [],
}
