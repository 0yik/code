# -*- coding: utf-8 -*-
{
    'name': 'Urgent Leave Type Extended',
    'version': '1.0',
    'category': 'Leave Management',
    'sequence': 13,
    'summary': 'setup for leave request',
    'description': "This module includes setup for urgent leave request by overriding leave days limit function",
    'website': 'www.hashmicro.com',
    'author': 'HashMicro / Janbaz Aga',
    'depends': [
       'hr_holidays','leave_days_limit'
    ],
    'data': [
        'data/holiday_status.xml',
        'views/hr_holidays_view.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}