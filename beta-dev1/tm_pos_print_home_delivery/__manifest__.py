{
    'name' : 'tm_pos_print_home_delivery',
    'version' : '1.0',
    'category': 'Point of sale',
    'author': 'HashMicro / Viet',
    'description': """tm_pos_print_home_delivery
    """,
    'website': 'www.hashmicro.com',
    'depends' : ['base','point_of_sale','pos_home_delivery'],
    'data': [
		'views/views.xml',
        'views/report_template.xml',
        'views/report.xml'
    ],
    'demo': [
    ],
    'qweb': [
	'static/src/xml/*.xml',
    ],
}
