# -*- coding: utf-8 -*-
{
    'name': "HR Disciplinary",

    'summary': """
        The purpose of this module is to record disciplinary action
        for dealing with job-related behavior that does not meet expected
        and communicated performance standards.
        """,

    'description': """
        The purpose of this module is to record disciplinary action for 
        dealing with job-related behavior that does not meet expected and 
        communicated performance standards.
    """,

    'author': "Hashmicro/Kuldeep",
    'website': "http://www.hashmicro.com",

    'category': 'Human Resources',
    'version': '0.1',

    'depends': ['base', 'hr'],

    'data': [
        # 'security/ir.model.accesss/''''.csv',
        'data/data.xml',
        'wizards/wizard.xml',
        'wizards/disciplinary_wizard.xml',
        'views/employee.xml',
        'views/views.xml',
        'views/templates.xml',
    ],
}