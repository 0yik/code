# -*- coding: utf-8 -*-

{
    'name': 'FMD Restrict Export Data',
    'version': '1.0',
    'category': 'base',
    'description': """
This module restrict export data of users.
    """,
    'author': "Hashmicro / Bhavik-TechnoSquare",

    'website': "www.hashmicro.com",
    'depends': [
        'base',
        'web',
        'base_setup'
    ],
    'data': [
        'view/restrict_export_view.xml'
    ],

    'installable': True,
    'active': False,
    'application': True,
}
