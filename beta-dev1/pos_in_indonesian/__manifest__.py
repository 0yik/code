{
    'name' : 'pos_in_indonesian',
    'version' : '1.0',
    'category': 'Point of sale',
    'author': 'HashMicro / Viet',
    'description': """pos_in_indonesian, load language indo before using.
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
