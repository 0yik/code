{
    'name': "POS Sync Sessions",
    'version': '2.1',
    'category': 'Point of Sale',
    'author': 'TL Technology',
    'sequence': 0,
    'summary': 'POS Sync Sessions',
    'description': """
    We're have sessions run on the current time \n
    And module support for syncing another sessions current times : syncing product, client add, quantity, discount or something like that \n
    ....
    """,
    'depends': ['point_of_sale', 'pos_base'],
    'data': [
        'security/ir.model.access.csv',
        'template/__import__.xml',
        'view/pos.xml',
    ],
    'demo': ['demo/demo.xml'],
    'qweb': [
        'static/src/xml/*.xml'
    ],
    'price': '200',
    'website': 'http://posodoo.com',
    "currency": 'EUR',
    'application': True,
    'images': ['static/description/icon.png'],
    'support': 'thanhchatvn@gmail.com'
}
