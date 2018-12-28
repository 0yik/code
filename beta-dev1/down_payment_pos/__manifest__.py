{
    'name' : 'down payment pos',
    'version' : '1.0',
    'category': 'Point of sale',
    'author': 'HashMicro / Viet',
    'description': """down payment pos
    """,
    'website': 'www.hashmicro.com',
    'depends' : ['base','point_of_sale','sarangoci_account_deposit'],
    'data': [
		'views/views.xml',
    ],
    'demo': [
    ],
    'qweb': [
	'static/src/xml/*.xml',
    ],
}