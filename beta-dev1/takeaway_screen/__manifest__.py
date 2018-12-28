{
    'name': 'Take Away acreen',
    'sequence': 0,
    'version': '1.0',
    'author': 'HashMicro/ MP Technolabs-Purvi',
    'description': 'POS Take Away Screen',
    'category': 'Point of Sale',
    'depends': ['complex_kds'],
    'data': [
        'template/__import__.xml',
        'views/pos_view.xml',
    ],
    'demo': [],
    'qweb': [
    'static/src/xml/takeaway.xml'
    ],
    'installable': True,
    'application': True,
}
