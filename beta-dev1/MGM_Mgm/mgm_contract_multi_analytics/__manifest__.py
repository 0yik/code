# -*- coding: utf-8 -*-
{
	'name' : 'Mgm Contract Multi Analytics',
	'version' : '1.0',
	'category': 'sales',
	'author': 'Hashmicro/GYB IT SOLUTIONS-Anand/ MP Technolabs - Vatsal/',
	'description': """ 	""",
	'website': 'http://www.hashmicro.com/',
	'depends' : [
		'sale','so_blanket_order','multi_level_analytical','enterprise_accounting_report','mgm_sales_contract',
		'mgm_multi_assign_analytics','account',
	],
	'data': [
	    'views/mgm_multi_assign_analytics.xml',
		'views/invoice_view.xml',
	],
	'demo': [
	],
	'installable': True,
	'application': True,
	'auto_install': False,
}
