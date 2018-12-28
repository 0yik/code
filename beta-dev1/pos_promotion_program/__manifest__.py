# -*- coding: utf-8 -*-
{
    'name': "POS Promotion Program",
    'version':'1.0',
    'category': 'POS',
    'author': 'Hashmicro/ MP Technolabs - Parikshit Vaghasiya',
    'description': """
        Pos promosion program module.
    """,
    'website': 'www.hashmicro.com',
    'category': 'pos promotion',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['pos_promotion', 'program_branch_assignment', 'branch','pos_base'],

    # always loaded
    'data': [
        'wizard/import_product_wizard_view.xml',
        'views/program_promotion_config_view.xml',
        
    ],
    'qweb': [
        'static/src/xml/*.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
    'application': True,
}
