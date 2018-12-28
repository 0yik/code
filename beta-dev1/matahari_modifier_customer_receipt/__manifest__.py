# -*- coding: utf-8 -*-
{
    'name': 'Matahari Modifier Customer Receipt',
    'author': 'HashMicro/Abulkasim Kazi',
    'version': '1.0',
    'summary': 'customer and supplier payment',
    'description': 'create modifier based on customer receipt and supplier payment.',
    'website': 'www.hashmicro.com',
    'category': 'account',
    'depends': ['account_accountant', 'sg_partner_payment'],
    'data': [
        'security/ir.model.access.csv',
        'wizard/receipt_payment_view.xml',
        'views/receipt_payment_view.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}