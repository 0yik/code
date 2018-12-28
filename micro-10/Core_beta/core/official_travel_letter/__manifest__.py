# -*- coding: utf-8 -*-
{
    'name': "Official Travel Letter",

    'summary': """
        Official Travel Letter""",

    'description': """
        This module add the functionality to give Official Travel Letter to employee. 
    """,

    'category': 'HR',
    'version': '1.0',

    # any module necessary for this one to work correctly
    'depends': ['hr_attendance'],

    # always loaded
    'data': [
        'views/official_travel_view.xml',
        'data/travel_sequence.xml',
        'report/official_travel_report.xml',
        'security/ir.model.access.csv'
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}