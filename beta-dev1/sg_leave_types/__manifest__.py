# -*- coding: utf-8 -*-
{
    'name': 'Leave Type',
    'version': '1.0',
    'category': 'Leave Management',
    'sequence': 13,
    'summary': 'setup for leave request',
    'description': "This module includes setup for urgent leave request by overriding leave days limit function",
    'website': 'www.mptechnolabs.com',
    'author': 'Bharat Chauhan',
    'depends': [
        'leave_days_limit', 'sg_hr_holiday', 'sg_allocate_leave','propell_modifier_urgent_leave', 'hr_holidays'
    ],
    'data': [
        'data/hide_menu.xml',
        'views/hr_holidays_view.xml',
        'data/leave_approval_email_template.xml',
        'security/security.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}