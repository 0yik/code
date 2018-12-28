{
    'name': 'Salary Late Rules',
    'description': 'This module will modify Salary Rule related to  Attendance',
    'category': 'Payroll',
    'version': '1.0',
    'author': 'HashMicro / MP Technolabs(chankya)',
    'website': 'www.hashmicro.com',
    'depends': ['l10n_sg_hr_payroll','sg_hr_config'],
    'data': [
        'views/hr_config_setting_view.xml',
        'views/payroll_extended_view.xml',
        'data/salary_rule.xml',
    ],
    'application': False,
    'installable': True,
}