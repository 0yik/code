{
    'name': 'POS Order Return Modifier',
    'sequence': 0,
    'version': '2.0',
    'author': 'HashMicro/ MP Technolabs-Purvi / Viet',
    'description': 'Removes Return Cancel Button when its on Floor Screen',
    'category': 'Point of Sale',
    'depends': ['pos_order_return', 'pos_restaurant'],
    'data': [
        'template/__import__.xml',
        'views/register.xml',
        'views/res_users_view.xml'
    ],
    'demo': [],
    'qweb': [
        'static/src/xml/*.xml',
    ],
    'installable': True,
    'application': True,
}
