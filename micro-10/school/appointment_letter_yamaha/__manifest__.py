# -*- coding: utf-8 -*-
{
    'name': "Appointment Letter Yamaha",

    'summary': """
        Appointment Letter Yamaha""",

    'description': """
        This module add the functionality to give contract Appointment Letter to employee. 
    """,

    'category': 'HR',
    'version': '1.0',

    # any module necessary for this one to work correctly
    'depends': ['sg_hr_employee','hr_contract'],

    # always loaded
    'data': [
        'report/apt_letter_yamaha.xml',
        'data/paperformat.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}