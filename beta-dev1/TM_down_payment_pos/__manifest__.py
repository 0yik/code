{
    'name' : 'TM down payment pos',
    'version' : '1.0',
    'category': 'Point of sale',
    'author': 'HashMicro / Viet',
    'description': """TM down payment pos
    """,
    'website': 'www.hashmicro.com',
    'depends' : ['base','point_of_sale','tm_account_deposit'],
    'data': [
		'views/views.xml',
    ],
    'demo': [
    ],
    'qweb': [
	'static/src/xml/*.xml',
    ],
}