# -*- coding: utf-8 -*-
{
    'name': 'Booking Modifier',
    'summary': 'Booking modifier for hashmicro internal',
    'description': 'Booking modifier changes required for hashmicro internal',
    'author': 'Hashmicro/Saravanakumar',
    'website': 'https://www.hashmicro.com/',
    'category': 'Bookings',
    'version': '0.1',
    'sequence': 30,
    'depends': ['hilti_modifier_customer_booking'],
    'data': [
        'views/anchor_views.xml',
    ],
    'application': True,
    'installable': True,
}