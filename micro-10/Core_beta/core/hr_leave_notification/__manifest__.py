{
    'name': 'HR leave Notification',
    'description': 'This module will add feature to send mail to leave manager of Employee',
    'category': 'HR',
    'version': '1.0',
    'author': 'HashMicro / MP Technolabs',
    'website': 'www.hashmicro.com',
    'depends': ['hr_holidays'],
    'data': [
        'data/hr_holidays_email_template.xml',
    ],
    'application': True,
    'installable': True,
}