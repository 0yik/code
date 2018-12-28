# -*- coding: utf-8 -*-
{
    'name': "franchise_management",

    'summary': """Manage franchise with royalty rates""",

    'description': """Manage franchise with royalty rates""",
    'sequence': 1,
    'author': "HashMicro / Shyam",
    'website': "http://www.hashmicro.com",
    'version': '1.0',
    # any module necessary for this one to work correctly
    'depends': ['school_fees'],
    # always loaded
    'data': [
        'views/royalti_fees_view.xml',
        'security/ir.model.access.csv',
        'views/models_views.xml',
    ],
    'demo': [
    ],
}