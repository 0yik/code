# -*- coding: utf-8 -*-
{
    'name': 'Leave Manager Approval',
    'version': '1.0',
    'category': 'Leave Management',
    'sequence': 11,
    'summary': 'setup for leave manager approval process',
    'description': "This module includes leave manager approval process related to given level",
    'website': 'http://www.axcensa.com/',
    'author': 'Axcensa',
    'depends': [
        'hr_holidays'
    ],
    'data': [
        'views/hr_views.xml',
        'views/hr_holidays_view.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}