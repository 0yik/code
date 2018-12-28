{
    'name' : 'Pos config receipt symbol',
    'version' : '1.0',
    'category': 'Point of sale',
    'author': 'HashMicro / Viet',
    'description': """Pos config receipt symbol.
    """,
    'website': 'www.hashmicro.com',
    'depends' : ['base','point_of_sale'],
    'demo': [
    ],
    'qweb': [
	'static/src/xml/*.xml',
    ],
    'data': [
        'views/pos_config.xml',
        'views/views.xml'
    ],
}
