# -*- coding: utf-8 -*-
{
    'name': 'Leave Days Limit',
    'version': '1.0',
    'category': 'Leave Management',
    'sequence': 12,
    'summary': 'setup for leave days limit of leave request',
    'description': "This module includes setup for leave days limit of leave request based on given no. of days",
    'website': 'http://www.axcensa.com/',
    'author': 'Axcensa',
    'depends': [
        'leave_manager_approval','sg_hr_holiday'
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/leave_days_limit_view.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}