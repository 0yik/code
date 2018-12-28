{
    'name': 'POS Product List View',
    'description': 'Product Show in list view in Pont of Sale',
    'author': "HashMicro/ Janbaz Aga",
    'license': '',
    'summary': """It will show product in list view""",
    'category': 'Point of Sale',
    'website': '',
    'images': [],
    'depends': ['point_of_sale'],
    'demo': [],
    'data': [
                'views/pos_config.xml',
                'views/point_of_sale.xml',
             ],
    'qweb': [
        'static/src/xml/pos.xml'
    ],
    'active': False,
    'installable': True,
    'application': True,
}