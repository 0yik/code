# -*- coding: utf-8 -*-
{
    'name': "Modifier TEO Accounting",
    'summary': """
        Customized Accounting Reports & View
    """,
    'description': """
    """,
    'author': "Hashmicro / MpTechnolabs - Bhavin Jethva, Komal Kaila",
    'website': "www.hashmicro.com",
    'category': 'Accounting',
    'version': '1.0',
    'depends': ['sg_partner_payment','sg_expensevoucher', 'account_journal_entry_base_currency','accounting_xls_reports'],
    'data': [
        'data/data.xml',
        'report_menu.xml',
        'views/layouts.xml',
        'wizard/account_report_aged_partner.xml',
        'report/account_general_ledger.xml',
        'report/journal_entries_report.xml',
        'report/account_voucher_report.xml',
        'report/customer_receipt_report.xml',
        'report/aged_partner_balance.xml',
        'views/account_invoice_view.xml',
    ],
    'installable': True,
}