# -*- coding: utf-8 -*-
{
    'name': 'Contract Attachments',
    'summary': 'Add attachment tab to the Contract',
    'description': 'Contract Attachments : allow users to Add attachments in to the Contract',
    'version': '1.0',
    'category': 'Sale',
    'author': 'Hashmicro/Saravanakumar',
    'website': 'www.hashmicro.com',
    'depends': ['stable_account_analytic_analysis'],
    'data': [
        'security/ir.model.access.csv',
        'views/analytic_view.xml',
    ],
    'application': True,
}
