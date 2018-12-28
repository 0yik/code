# -*- encoding: utf-8 -*-
{
    'name': 'HAM Project Report',
    'version': '1.0',
    'category': 'Report',
    'author': 'HashMicro / TriNguyen',
    'description': """
        Making reports for Tax Invoice, Commercial Invoice, Delivery Orders, Quotation, Purchase Orders
                """,
    'website': 'www.hashmicro.com',
    'depends': ['account','purchase','sale','stock'],
    'data': [
        'report/invoice_tax_templates.xml',
        'report/delivery_order_templates.xml',
        'report/quotation_order_templates.xml',
        'report/purchase_order_templates.xml',
        'report/commercial_invoice_templates.xml',
    ],
    'images':['static/img/signature.png',],
}
