# -*- coding: utf-8 -*-
{
    'name': "Payment Voucher",
    'summary': """
        Payment Voucher Function for Accounting Purchases.""",
    'description': """
        Payment Voucher Function for Accounting Purchases.
    """,
    'author': "HashMicro/Techultra Solutions - Mustufa Kantawala",
    'website': "http://www.hashmicro.com",
    'category': 'Accounting',
    'version': '0.1',
    'depends': ['account','account_accountant', 'sg_expensevoucher', 'purchase'],
    'data': [
        'security/ir.model.access.csv',
        'data/ir_sequence_data.xml',
        'report/report.xml',
        'report/payment_voucher_report.xml',
        'views/purchase_payment_voucher.xml',
        
    ],
    'demo': [],
    'installable': True,
    'auto_install': False,
}
