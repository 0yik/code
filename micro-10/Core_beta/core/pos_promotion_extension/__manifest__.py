{
    'name': "POS Promotions Extension",
    'version': '2.0',
    'category': 'Point of Sale',
    'author': 'TL Technology',
    'sequence': 0,
    'summary': 'POS Promotions Extension',
    'description': 'POS Promotions Extension',
    'depends': ['pos_base','pos_promotion'],
    'data': [
        'view/pos_order.xml',
        'view/pos_promotion.xml',
        '__import__/template.xml',
    ],
    'qweb': [
        # 'static/src/xml/*.xml'
    ],
    'author': "HashMicro / Duy",
    'website': "http://www.hashmicro.com",
    'images': ['static/description/icon.png'],
}
