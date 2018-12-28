# -*- coding: utf-8 -*-
{
    'name': 'Manpower Planning',
    'version': '1.0',
    'category': 'Human Resources',
    'sequence': 20,
    'summary': 'setup for company can do manpower planning and analysis based on existing and recruiting manpower.',
    'description': "This module includes setup for company can do manpower planning and analysis based on existing and recruiting manpower.",
    'website': 'http://www.hashmicro.com/',
    'author': 'Hashmicro/Kannan',
    'depends': [
        'hr_recruitment', 'sg_hr_employee',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/manpower_planning_view.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}