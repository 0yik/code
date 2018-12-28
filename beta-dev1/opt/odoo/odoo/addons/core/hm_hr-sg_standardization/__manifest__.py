# -*- coding: utf-8 -*-
{
    'name': 'Hm Hr Sg Standardization',
    'version': '1.0',
    'category': 'Human Resources',
    'sequence': 15,
    'summary': 'To edit the fields while creating an employee. (Employee form)',
    'description': "This module includes setup to add and do changes in employee form fields",
    'website': 'http://www.hashmicro.com/',
    'author': 'Hashmicro/Kannan',
    'depends': [
        'sg_hr_employee','sg_holiday_extended','sg_ir21'
    ],
    'data': [
        'views/hr_view.xml',
        'views/hr_view_extended.xml',
#        'security/ir.model.access.csv',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}