# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
	'name' : 'MGM Budget Management Modifier',
	'version' : '1.0',
	'category': 'account',
	'author': 'Hashmicro/MP Technolabs / Vatsal',
	'description': """ MGM Budget Management Modifier .	""",
	'website': 'http://www.hashmicro.com/',
	'depends' : ['account_budget','budget_management','budget_management_AA'],
	'data': [
	    'views/budget_view.xml',
	],
	'demo': [
	],
	'installable': True,
	'application': True,
	'auto_install': False,
}
