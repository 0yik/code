# -*- coding: utf-8 -*-
{
    'name': 'Propell Leave Recovery',
    'version': '1.0',
    'category': 'Leave Management',
    'sequence': 13,
    'summary': 'Leave Recovery',
    'description': "Allows users to recover their leaves which have been submitted earlier as leave requests, and approve that leave base on leave approval hierarchy",
    'website': 'www.mptechnolabs.com',
    'author': 'Bharat Chauhan',
    'depends': [
        'hr', 'hr_holidays', 'modifier_leave_recovery'
    ],
    'data': [
        'views/hr_holidays_recovery_view.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}