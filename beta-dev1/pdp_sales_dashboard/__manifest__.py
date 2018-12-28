# -*- coding: utf-8 -*-
{
    'name' : 'PDP Sales Dashboard',
    'version' : '1.0',
    'category': 'sale',
    'author': 'Hashmicro/GYB IT SOLUTIONS-Anand',
    'description': """ Create Dashboard for Sales
    """,
    'website': 'http://www.hashmicro.com/',
    'depends' : [
	'sale', 'sales_team', 'crm',
    ],
    'data': [
    'views/pdp_sale_dashboard.xml',
    ],
    'demo': [
    ],
    'qweb': ["static/src/xml/pdp_sales_dashboard.xml"],
    'installable': True,
    'application': True,
    'auto_install': False,
}
