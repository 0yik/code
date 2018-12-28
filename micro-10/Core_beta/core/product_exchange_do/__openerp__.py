{
    'name': "Product Exchange on DO",
    'version': '0.1',
    'category': 'sale',
    'description': """
        1. Allow User to Exchange Product on Delivery order
    """,
    'author': "Hashmicro / Parikshit Vaghasiya",
    'website': "http://www.hashmicro.com",
    'depends': ['sale','stock'],
    'data': [
        'wizard/product_exchange_wizard_view.xml',
        'views/product_exchange_do_view.xml',
        
    ],
    'qweb': [
        "static/src/xml/*.xml",
    ],
}