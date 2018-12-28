{
    'name' : 'Loyalty reports',
    'version' : '1.0',
    'category': 'pos',
    'author': 'HashMicro / Viet',
    'description': """
    """,
    'website': 'www.hashmicro.com',
    'depends' : ['base','pos_loyalty','pizzahut_loyalty_history','point_of_sale'],
    'data': [
        'views/views.xml'
    ],
    'demo': [
    ],
    'qweb': [
	   'static/src/xml/*.xml',
    ],
}