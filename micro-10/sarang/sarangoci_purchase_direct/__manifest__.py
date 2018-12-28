# -*- coding: utf-8 -*-
{
    'name' : 'Sarangoci Direct Purchase',
    'version' : '1.0',
    'category': 'Point of sale',
    'author': 'HashMicro / TechUltra Solutions / Krutarth',
    'description': """This module allows to allow Purchase Direct
    """,
    'website': 'www.techultrasolutions.com',
    'depends' : ['purchase'],
    'data': [
        'data/sequence_data.xml',
        'views/res_partner_modifications.xml',
        'views/purchase_direct_modifications.xml',
    ],
    'demo': [

    ],
    'qweb': [

    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
