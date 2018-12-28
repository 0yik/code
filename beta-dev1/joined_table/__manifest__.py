# -*- coding: utf-8 -*-
{
    'name': 'Joined Table',
    'version': '1.0',
    'category': 'Point Of Sale',
    'author': 'HashMicro/ MPTechnolabs - Komal Kaila',
    'website': "http://www.hashmicro.com",
    'summary': 'Joined Table',
    'depends': [
        'point_of_sale', 'pos_bus_restaurant','pos_restaurant_base'
    ],
    'data': [
        'views/pos_registration.xml',
    ],
    'qweb': ['static/src/xml/pos.xml'],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'AGPL-3',
}
