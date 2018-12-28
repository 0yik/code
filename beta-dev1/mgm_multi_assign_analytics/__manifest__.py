# -*- coding: utf-8 -*-
{
	'name' : 'Mgm Multi Assign Analytics',
	'version' : '1.0',
	'category': 'sales',
	'author': 'Hashmicro/GYB IT SOLUTIONS-Anand / MP Technolabs / Vatsal',
	'description': """ 	""",
	'website': 'http://www.hashmicro.com/',
	'depends' : [
		'sale', 'multi_level_analytical', 'enterprise_accounting_report',
	],
	'data': [
	    'data/data_account_analytic_level.xml',
		'wizard/mgm_multi_assign_analytics.xml',
	    'views/sale.xml',
		'views/analytic_level.xml',
	],
	'demo': [
	],
	'installable': True,
	'application': True,
	'auto_install': False,
}
