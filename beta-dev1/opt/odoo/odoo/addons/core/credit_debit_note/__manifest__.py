# -*- coding: utf-8 -*-
{
    'name': 'Credit & Debit Note',
    'version': '1.0',
    'category': 'Invoice',
    'sequence': 7,
    'summary': 'setup for credit & debit note sub menus for refund',
    'description': "This module includes setup for credit & debit note sub menus for refund",
    'website': 'http://www.axcensa.com/',
    'author': 'Axcensa',
    'depends': [
        'account_accountant'
    ],
    'data': [
        'data/data.xml',
        'wizard/invoice_debit_note.xml',
	'wizard/invoice_credit_note.xml',
        'views/account_invoice_view.xml',
		
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
