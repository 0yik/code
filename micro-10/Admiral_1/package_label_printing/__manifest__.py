# -*- coding: utf-8 -*-
{
    'name' : 'Package Label Printing',
    'version' : '1.1',
    'author' : 'HashMicro / Dipali',
    'summary': 'Print the Package Label',
    'sequence': 30,
    'description': """
    	Allow users to enter the details of label to be printed for deliveries and the number of label to be printed.
    """,
    'category': '',
    'website': 'www.hashmicro.com',
    'depends' : ['base', 'sale', 'stock', 'report'],
    'data': [
	'wizard/package_label_view.xml',
	'wizard/package_view.xml',
	'views/report_paperformat.xml',
	'views/package_label_report.xml',
	'views/report_package_label.xml',
    ],
    'demo': [
    ],
    'qweb': [
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
