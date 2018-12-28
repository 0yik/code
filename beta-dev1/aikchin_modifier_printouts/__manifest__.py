# -*- encoding: utf-8 -*-
{
    'name': 'Aikchin Project Report',
    'version': '1.0',
    'category': 'Report',
    'author': 'HashMicro / Quy / Duy',
    'description': """
        Making reports for Purchase Order, Tax Invoice, Credit Note, Debit Note,
                """,

    'depends': [
        'base',
        'account',
        'purchase',
        'sale',
        'stock',
        'point_of_sale',
        'sg_hr_employee',
    ],

    'data': [
#         'views/tax_invoice_view.xml',
#         'views/res_partner_bank.xml',
#         'views/customer_soa.xml',
#         'views/debit_note.xml',
#         'views/credit_note.xml',
        'data/data.xml',
        'report/sale_order_templates.xml',
        'report/layouts.xml',
        'views/product_template.xml',
        'report/purchase_order_templates.xml',
        'report/purchase_order_no_price_templates.xml',
        'report/layouts_2.xml',
        'report/customer_invoice_template.xml',
        'report/pos_cash_template.xml',
        'report/quotation_template.xml',
        'report/delivery_order_template.xml',
        'report/delivery_order_no_price_template.xml',
        'report/good_returned_note.xml',
        'report/report_partnerledger.xml',
        'report/aikchin_appraisal.xml',
        'report/modifier_partner_ledger_report.xml',
        'views/aikchin_appraisal.xml'

    ],
    'qweb': ['static/xml/pos_label.xml'],

}
