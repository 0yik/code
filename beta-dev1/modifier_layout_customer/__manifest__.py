# -*- coding: utf-8 -*-
{
    'name': "modifier_layout_customer",



    'description': """
       This module changes address field in  partner form and set default lanaguage indonesia
       Last Updated 20-03-2018
    """,

    'author': "Hashmicro / MpTechnolabs - Prakash Nanda",
    'website': "http://www.mptechnolabs.com/",

    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['sale','vit_efaktur','vit_kelurahan'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/company_title_view.xml',
        'views/partner.xml',
        'views/modified_partner.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    "installable": True,
    "auto_install": False,
    "application": True,
}


