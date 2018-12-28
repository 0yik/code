{
    'name' : 'Pos sarangoci reprint',
    'version' : '1.0',
    'category': 'Point of sale',
    'author': 'HashMicro / Viet',
    'description': """Reprint confirmed order
    """,
    'website': 'www.hashmicro.com',
    'depends' : ['base','point_of_sale'],
    'data': [
		'views/views.xml',
    ],
    'demo': [
    ],
    'qweb': [
	'static/src/xml/*.xml',
    ],
}
