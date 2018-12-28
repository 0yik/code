# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
	'name' : 'Mgm Modifier Partner Payment',
	'version' : '1.0',
	'category': 'account',
	'author': 'Hashmicro/GYB IT SOLUTIONS-Anand',
	'description': """ Add Memo field in Customer receipt Debits and Credits line .	""",
	'website': 'http://www.hashmicro.com/',
	'depends' : [
		'account','sg_partner_payment','account_accountant',
	],
	'data': [
	    'views/receipt_payment.xml',
	],
	'demo': [
	],
	'installable': True,
	'application': True,
	'auto_install': False,
}
