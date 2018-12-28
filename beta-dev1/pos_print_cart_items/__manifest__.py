{
    'name': 'POS Print Cart Items',
    'description': 'Create a function to print list of products added into the shopping cart in the POS before payment.',
    'category': 'Report',
    'version': '1.0',
    'author': 'HashMicro / Janbaz Aga',
    'website': 'www.hashmicro.com',
    'depends': ['point_of_sale','branch','report'],
    'data': [
        'views/pos_cart_template.xml',
    ],
    'qweb': [
            'static/src/xml/*.xml',
        ],
    'application': True,
    'installable': True,
}