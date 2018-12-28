{
    'name': 'POS Kitchen Room',
    'sequence': 0,
    'version': '2.0',
    'author': 'HashMicro/ MP Technolabs-Purvi',
    'description': 'POS Restaurant Kitchen Screen Hierarchy',
    'category': 'Point of Sale',
    'depends': ['pos_restaurant_kitchen', 'product_order_category'],
    'data': [
        'template/__import__.xml',
        'security/ir.model.access.csv',
        'views/pos_view.xml',
    ],
    'demo': [],
    'qweb': [
    'static/src/xml/*.xml'
    ],
    'installable': True,
    'application': True,
}
