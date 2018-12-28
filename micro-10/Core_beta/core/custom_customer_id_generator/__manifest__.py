# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': ' Custom Customer ID Generator',
    'version': '1.1',
    'category': 'Project',
    'summary': 'Unique ID for Customers',
    'description': """
    This module generates unique ID for Customers 
    """,
    'author': 'HashMicro / GeminateCS',
    'website': 'www.hashmicro.com', 
    'depends': [
        'base',
        'account',
    ],
    'data': [
        'views/res_partner_view.xml',
        'views/account_invoice_view.xml',
        'views/account_payment_view.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}