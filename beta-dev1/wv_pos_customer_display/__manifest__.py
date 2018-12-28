# -*- coding: utf-8 -*-

{
    'name': 'POS Customer Display',
    'version': '1.0',
    'category': 'Point of Sale',
    'sequence': 6,
    'author': 'Webveer',
    'summary': 'Pos Customer screen allows you to show information in LCD display and do not require POS Box and also work on COM port.',
    'description': """
    
Pos Customer screen allows you to show information in LCD display and do not require POS Box and also work on COM port.

=======================

""",
    'depends': ['point_of_sale'],
    'data': [
        'views/views.xml',
        'views/templates.xml'
    ],
    'qweb': [
        'static/src/xml/pos.xml',
    ],
    'images': [
        'static/description/display.jpg',
    ],
    'installable': True,
    'website': '',
    'auto_install': False,
    'price': 100,
    'currency': 'EUR',
}
