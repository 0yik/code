{
    'name' : 'Pos print bill',
    'version' : '1.0',
    'category': 'Point of sale',
    'author': 'HashMicro / Viet',
    'description': """Pos print bill.
    """,
    'website': 'www.hashmicro.com',
    'depends' : ['base','point_of_sale'],
    'demo': [
    ],
    'qweb': [
	'static/src/xml/*.xml',
    ],
    'data': [
        'views/views.xml',
    ],
}
