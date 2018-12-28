# -*- coding: utf-8 -*-
{
    'name': "Term Of Payment Restrict",

    'description': """
        Sale,Invoice
    """,
    'author': 'HashMicro / Duy /Viet ',
    'website': 'www.hashmicro.com',

    'category': 'sale,invoice',
    'version': '1.0',

    'depends': ['account','sale'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/register.xml',
        'views/sale_report.xml',
        'views/sale_order.xml',
    ],
    # only loaded in demonstration mode
    'qweb': [],
    'demo': [
    ],
}