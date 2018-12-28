# -*- coding: utf-8 -*-
{
    'name': "Other Bills",
    'summary': """Separate customer invoice and other invoice, separate supplier bills and other bills.""",
    'author': "HashMicro/ MP Technolabs - Parikshit Vaghasiya",
    'website': "https://www.hashmicro.com/",
    'category': 'accounting',
    'version': '0.1',

    'depends': ['account'],

    'data': [
        'views/account_invoice_view.xml',
        'views/supplier_invoice_view.xml',
        'data/data.xml',
    ],

    'installable': True,
    'application': True,
    'auto_install': False,
}
