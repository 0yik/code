{
    'name': 'POS Kitchen Room',
    'sequence': 0,
    'version': '2.0',
    'author': 'TL Technology',
    'description': 'POS Restaurant Kitchen Screen',
    'category': 'Point of Sale',
    'depends': ['pos_bus_restaurant'],
    'data': [
        'template/__import__.xml',
        'view/pos.xml',
    ],
    'demo': ['demo/demo.xml'],
    'qweb': ['static/src/xml/*.xml'],
    'installable': True,
    'application': True,
    'price': '100',
    'website': 'http://posodoo.com',
    "currency": 'EUR',
    'images': ['static/description/icon.png'],
    'support': 'thanhchatvn@gmail.com'
}
