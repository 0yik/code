{
    'name': 'Assign Temp Order',
    'sequence': 0,
    'version': '1.0',
    'author': 'HashMicro/ MP Technolabs-Purvi / GYB IT SOLUTIONS-Anand',
    'description': 'Assign Temporary Order',
    'category': 'Point of Sale',
    'depends': ['pos_bus_restaurant', 'pos_restaurant_kitchen'],
    'data': [
        'template/__import__.xml',
        'views/pos_config_view.xml',
    ],
    'demo': [],
    'qweb': ['static/src/xml/*.xml'],
    'installable': True,
    'application': True,
}
