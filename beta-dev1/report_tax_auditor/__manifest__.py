# -*- coding: utf-8 -*-
{
    'name': "Report Tax Auditor",
    'description': "Report Menu for Auditor",
    'author': 'HashMicro / Quy / Saravanakumar',
    'website': 'www.hashmicro.com',
    'category': 'hr',
    'version': '1.0',
    'depends': ['point_of_sale','pos_combo','product','account', 'branch'],
    'data': [
        'views/report_menu_view.xml',
        'security/ir.model.access.csv',
        'wizards/pos_sale_report_view.xml',
        'data/product.xml',
        'data/journal.xml',
    ],
    'application':  True,
}