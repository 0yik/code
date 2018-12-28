# -*- coding: utf-8 -*-

{
    'name': 'Point of Sale Invoice Payment',
    'version': '1.0',
    'category': 'Point of Sale',
    'sequence': 6,
    'author': 'HashMicro/ MPTechnolabs - Komal Kaila',
    'website': "http://www.hashmicro.com",
    'summary': 'Set invocie status as paid',
    'description': """

When we select the invoice and make payment in POS, the invoice also will have the payment registered and payment journal entry is created as well.

""",
    'depends': ['point_of_sale'],
    'data': [
        'views/pos_view.xml',
    ],
    'qweb': [],
    'qweb': ['static/src/xml/pos_view.xml'],
    'images': [],
    'installable': True,
    'website': '',
    'auto_install': False,
    'price': 99,
    'currency': 'EUR',
}
