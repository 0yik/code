{
    'name': 'POS Kitchen Room',
    'sequence': 0,
    'version': '2.0',
    'author': 'HashMicro/ MP Technolabs-Purvi/ GYB IT Solutions-Anand',
    'description': 'POS Restaurant Kitchen Screen Modification',
    'category': 'Point of Sale',
    'depends': ['pos_restaurant_kitchen'],
    'data': [
        'template/__import__.xml',
        'security/ir.model.access.csv',
    ],
    'demo': [],
    'qweb': ['static/src/xml/*.xml'],
    'installable': True,
    'application': True,
}
