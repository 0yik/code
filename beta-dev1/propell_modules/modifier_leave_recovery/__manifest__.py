# -*- coding: utf-8 -*-
{
    'name': 'Leave Recovery',
    'version': '1.0',
    'category': 'Leave Management',
    'sequence': 13,
    'summary': 'Leave Recovery',
    'description': "Allows users to recover their leaves which have been submitted earlier as leave requests",
    'website': 'www.mptechnolabs.com',
    'author': 'Bharat Chauhan',
    'depends': [
        'hr', 'hr_holidays', 'sg_holiday_extended', 'sg_expire_leave'
    ],
    'data': [
        'security/hr_security.xml',
        'views/hr_holidays_recovery_view.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}