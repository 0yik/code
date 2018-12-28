# -*- coding: utf-8 -*-
{
    'name': 'Recruitment Checklist',
    'version': '1.0',
    'category': 'Human Resources',
    'sequence': 18,
    'summary': 'Setup onboarding checklist for each job position at Recruitment module.',
    'description': "This module includes Setup onboarding checklist for each job position at Recruitment module.",
    'website': 'http://www.hashmicro.com/',
    'author': 'Hashmicro/Kannan',
    'depends': [
        'hr_recruitment','employee_check_list'
    ],
    'data': [
        'views/job_position_view.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}