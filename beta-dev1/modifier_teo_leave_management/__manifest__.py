# -*- coding: utf-8 -*-
{
    'name': "Modifier Leave Management",
    'summary': """
        Leave Management""",
    'description': """
        Create Flow of Leave Management
    """,
    'author': "HashMicro / MpTechnolabs - Bhavin Jethva, Bhavik",
    'website': 'www.hashmicro.com',
    'category': 'Human Resources',
    'version': '1.0',
    'depends': ['hr_holidays', 'hr_dashboard', 'sg_holiday_extended'],
    'data': [
        'data/leave_management_data.xml',
        'views/notification_history_view.xml',
        'views/hr_holidays_view.xml',
        'views/hr_holiday_status_view.xml',
        'security/hr_leave_notification_security.xml',
        'security/ir.model.access.csv',
    ],
    "auto_install": False,
    "installable": True,
}
