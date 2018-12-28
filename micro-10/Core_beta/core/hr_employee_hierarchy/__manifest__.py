# -*- coding: utf-8 -*-
{
    'name': 'HR Employee Hierarchy',
    'version': '1.0',
    'category': 'Leave Management',
    'sequence': 13,
    'summary': 'setup for leave approval hierarchy',
    'description': "This module includes hierarchy for approve leave by different level of employee",
    'website': 'www.mptechnolabs.com',
    'author': 'Bharat Chauhan',
    'depends': [
        'hr', 'hr_holidays', 'sg_hr_holiday', 'sg_leave_types'
    ],
    'data': [
        'security/hr_security.xml',
        'security/ir.model.access.csv',
        'data/data.xml',
        'views/hr_holidays_view.xml',
        'views/notify_email_template.xml',
        'views/leave_approval_hierarchy.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}