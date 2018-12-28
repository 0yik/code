# -*- coding: utf-8 -*-
{
    "name": "Leave Approval Notification",
    "author": "HashMicro/ Amit Patel",
    "version": "1.0",
    'description': '''This module help to send a mail from the configuration to the Admin group once the employee leave is approved.''',
    'summary': 'Leave Approval Notification',
    "website": "www.hashmicro.com",
    "category": "HR Leave",
    "depends": ['sg_hr_holiday','school'],
    "data": [
		'data/ir_config_parameter_data.xml',
		'views/hr_leave_config_view.xml',
    ],
    "qweb": [],
    'demo': [],
    'installable': True,
    'auto_install': False,
}
