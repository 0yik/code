# -*- coding: utf-8 -*-
{
    'name' : 'MGM Sales Bar Chart',
    'version' : '1.0',
    'category': 'sale',
    'author': 'Hashmicro/GYB IT SOLUTIONS-Anand',
    'description': """ Create Bar Chart for Ferry, FLF, Tug and Barge, Stevedoring, Other Quotation, Total,
    """,
    'website': 'http://www.hashmicro.com/',
    'depends' : [
	'sale', 'sales_team', 'crm', 'so_blanket_order', 'account'],
    'data': [
        'security/ir.model.access.csv',
        'views/mgm_sales_bar_chart.xml',
        'data/sales_bar_chart_demo.xml',
    ],
    'demo': [
    ],
    'qweb': [
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
