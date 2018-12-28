# -*- coding: utf-8 -*-
{
    'name': 'Leave Allocation',
    'version': '1.0',
    'category': 'Leave Management',
    'sequence': 13,
    'summary': 'Leave Allocation',
    'description': "This module allcate leave to multiple employee, and skip leave allocation if employee will not meet to criteria.",
    'website': 'www.mptechnolabs.com',
    'author': 'Bharat Chauhan',
    'depends': [
        'hr', 'sg_leave_types', 'sg_allocate_leave'
    ],
    'data': [
        'views/hr_leave_allocation.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}