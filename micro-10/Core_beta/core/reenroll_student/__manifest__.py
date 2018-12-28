# -*- coding: utf-8 -*-
{
    'name': "reenroll_student",

    'summary': """User can re-enroll student after student state = terminate/alumni""",

    'description': """User can re-enroll student after student state = terminate/alumni""",
    'sequence': 1,
    'author': "HashMicro / Shyam",
    'website': "http://www.hashmicro.com",
    'version': '1.0',
    # any module necessary for this one to work correctly
    'depends': ['school'],
    # always loaded
    'data': [
        'views/models_views.xml',
    ],
    'demo': [
    ],
}