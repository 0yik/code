# -*- coding: utf-8 -*-
{
	'name' : 'Mgm Purchase Multi Analytics',
	'version' : '1.0',
	'category': 'purchase',
	'author': 'Hashmicro / MP Technolabs / Vatsal',
	'description': """ Mgm Purchase Multi Analytics	""",
	'website': 'http://www.hashmicro.com/',
	'depends' : [
		'purchase','so_blanket_order','enterprise_accounting_report','mgm_sales_contract',
		'mgm_multi_assign_analytics','account','purchase_requisition',
	],
	'data': [
	    'views/purchase_view.xml',
		'views/invoice_view.xml',
	],
	'demo': [
	],
	'installable': True,
	'application': True,
	'auto_install': False,
}
