# -*- coding: utf-8 -*-
{
    'name': "Payment Voucher Printout",
    'summary': """
        Payment Voucher Printout""",
    'description': """
        Print the report of sales receipts
    """,
    'author': "HashMicro/MP Technolabs - Komal Kaila",
    'website': "http://www.hashmicro.com",
    'category': 'Accounting',
    'version': '0.1',
    'depends': ['account','account_voucher', 'report', 'sg_partner_payment'],
    'data': [
        'data/payment_data.xml',
        'views/account_voucher_view.xml',
        'views/account_invoice_view.xml',
        'views/receipt_payment_view.xml',
        'reports/payment_voucher_report_view.xml',
        'reports/payment_voucher_report.xml',
        'reports/receipt_payment_report_view.xml',
        'reports/receipt_invoice_report_view.xml',
    ],
    'demo': [],
    'installable': True,
    'auto_install': False,
}
