# -*- coding: utf-8 -*-
# Copyright (C) Kanak Infosystems LLP.

{
    'name': 'Pos Birthday Discount',
    'version': '1.0',
    'summary': 'pos birthday discount',
    'images': ['static/description/main_img.png'],
    'description': """
get promotion on birthdaymonth
================================
    """,
    'author': 'Kanak Infosystems LLP.',
    'website': 'http://www.odooshoppe.com/',
    'category': 'Point of Sale',
    'depends': ['point_of_sale'],
    'data': [
        'views/birthday_reward.xml',
        'views/birthday_reward_templates.xml',
    ],
    'qweb': [
        'static/src/xml/pos.xml',
    ],
    'installable': True,
    'price' : 30,
    'currency': 'EUR',
    'live_test_url': 'https://youtu.be/HJaj9m4tl0c',
}
