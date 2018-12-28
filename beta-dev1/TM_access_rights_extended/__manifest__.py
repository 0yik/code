# -*- coding: utf-8 -*-
{
    'name': "TM Access rights",

    'summary': """
        Access rights group for pos, sales , purchase , inventory, accounting""",

    'description': """
        Access rights group for pos, sales , purchase , inventory, accounting
    """,

    'author': "Hashmicro / MP Technolabs - Parikshit Vaghasiya",
    'website': "http://www.hashmicro.com",

    'category': 'Access Rights',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'sale','account','purchase','point_of_sale','pos_home_delivery'],

    # always loaded
    'data': [
        'security/tokomadju_security.xml',
        'security/pos_access.xml',
        'security/ir.model.access.csv',
        'data/access_rights_group_data.xml',
        'views/menu.xml',
        'views/tokomodju_views.xml',
        
    ],
}
