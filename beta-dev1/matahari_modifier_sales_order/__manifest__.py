# -*- coding: utf-8 -*-
{
	"name": "Matahari Modifier Sales Order",
	"version": "1.0",
	"depends": [
		'sale','dynamic_product_code',
	],
	'images': [],
	"author": "Hashmicro / Quy",
	"website": "www.hashmicro.com",
	"summary": "",
	"description": """
""",
	"data": [
            'data/ir_sequence_data.xml',
            'views/sale_order_view.xml',
            'views/res_company_views.xml',
			'views/sale_order_line_view.xml'
	],
	# "application": True,
	"installable": True,
	"auto_install": False,
}
