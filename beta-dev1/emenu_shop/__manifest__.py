# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
	'name' : 'Emenu Shop',
	'version' : '1.0',
	'category': 'account',
	'author': 'Hashmicro/GYB IT SOLUTIONS-Anand',
	'website': 'http://www.hashmicro.com/',
	'depends' : [
		'product','point_of_sale','website_sale',
	],
	'data': [
	    'data/emenu_shop_data.xml',
	    #'views/product_extra_category.xml',
	    'views/emenu_shop_template.xml',
	],
	'demo': [
	],
	'installable': True,
	'application': True,
	'auto_install': False,
}
