# -*- coding: utf-8 -*-
{
    'name': 'Flexible Working Schedule',
    'version': '1.0',
    'category': 'Human Resources',
    'sequence': 17,
    'summary': '1. Enhance the working schedule to have "Alternate Week" function. For example, employees work on 1st and 3rd Saturday every month.'
               '2. Develop flexible working schedule for part timer.',
    'description': "This module includes setup to develop flexible working schedule for part timer.",
    'website': 'http://www.hashmicro.com/',
    'author': 'Hashmicro/Kannan',
    'depends': [
        'sg_holiday_extended'
    ],
    'data': [
        'views/resource_view.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}