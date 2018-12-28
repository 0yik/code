# -*- encoding: utf-8 -*-
{
    'name': 'Beumer Project Report',
    'version': '1.0',
    'category': 'Report',
    'author': 'HashMicro / Quy',
    'description': """
        Making reports for Tax Invoice, Credit Note, Debit Note, Customer SOA
                """,
    'website': 'www.hashmicro.com',
    'depends': ['base','account','purchase','sale','stock','hr_expense'],
    'data': [
        'views/tax_invoice_view.xml',
        'views/res_partner_bank.xml',
        'views/customer_soa.xml',
        'views/debit_note.xml',
        'views/credit_note.xml',
        'views/expense_report.xml',
        'report/purchase_order_templates.xml',
        'report/layouts.xml',
        'report/purchase_request_templates.xml',
        'report/layouts_2.xml'
    ],

}
