{
    'name': 'POS Table Arrangement',
    'version': '1.0',
    'summary': 'POS Restaurant Seating Arrangements',
    'description': 'It will allows you to arrange seating for POS Restaurants',
    'author': 'Hashmicro/Muthulakshmi',
    'website': 'www.hashmicro.com',
    'category': 'Point of Sale',
    'depends': ['pos_restaurant', 'pos_product_package'],
    'data': [
        'views/define.xml',
    ],
    'qweb': [
        'static/src/xml/*.xml'
    ],
    'installable': True,
    'application': True,
}
