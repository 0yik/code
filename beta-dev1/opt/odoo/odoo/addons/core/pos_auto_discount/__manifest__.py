{
    'name': 'POS auto discount filter by quantity',
    'sequence': 0,
    'version': '1.4',
    'author': 'TL Technology',
    'description': """
    - Auto discount filter by quantity \n
    - Eg: \n
        + by x(qty) price 100 USD / unit\n
        + by y(qty) price 50 USD / unit\n
    """,
    'category': 'Point of Sale',
    'depends': ['pos_base'],
    'data': [
        'security/ir.model.access.csv',
        '__import__/template.xml',
        'view/pos_discount.xml',
        'data/schedule.xml',
        'data/product.xml',
    ],
    'qweb': ['static/src/xml/*.xml'],
    'installable': True,
    'application': True,
    'price': '50',
    'website': 'http://posodoo.com',
    "currency": 'EUR',
    'images': ['static/description/icon.png'],
    'license': 'LGPL-3',
    'support': 'thanhchatvn@gmail.com'
}
