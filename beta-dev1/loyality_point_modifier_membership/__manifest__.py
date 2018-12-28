# -*- coding: utf-8 -*-
{
    'name': "POS Loyality Point Modifier Membership",
    'version':'1.0',
    'category': 'POS',
    'author': 'Hashmicro/ MP Technolabs - Parikshit Vaghasiya',
    'description': """
        loyality_point_modifier_membership module.
    """,
    'website': 'www.hashmicro.com',
    'category': 'pos promotion',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['pos_loyalty'],

    # always loaded
    'data': [
        'views/loyality_point_membership_view.xml',
    ],
    'qweb': [
        'static/src/xml/*.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
    'application': True,
}
