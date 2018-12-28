{
    'name': 'Attendance Auto Timesheet',
    'description': 'This module will create auto timesheet',
    'category': 'HR',
    'version': '1.0',
    'author': 'HashMicro / MP Technolabs(chankya)',
    'website': 'www.hashmicro.com',
    'depends': ['hr_timesheet_attendance','sg_hr_config','stable_hr_timesheet_invoice'],
    'data': [
        'views/hr_config_setting_view.xml',
        'data/timesheet_cron_data.xml',
    ],
    'application': False,
    'installable': True,
}