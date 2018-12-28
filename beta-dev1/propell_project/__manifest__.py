# -*- coding: utf-8 -*-
{
    'name': "propell_project",

    'summary': """
        This module will add supervisor field and team member for that project as order lines  to the project""",


    'author': "Hashmicro / MpTechnolabs - Prakash Nanda",
    'website': "www.mptechnolabs.com",

    'category': 'Project',
    'version': '1.0',

    # any module necessary for this one to work correctly
    'depends': ['project'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}