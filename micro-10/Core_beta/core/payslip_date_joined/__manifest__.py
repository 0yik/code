# -*- coding: utf-8 -*-
{
    'name': 'Payslip Date Joined',
    'description': 'This module is to create payslip based on employee Joined date',
    'version': '1.0',
    'category': 'Payroll',
    'author': 'HashMicro/ MPTechnolabs(Chankya)',
    'website': "http://www.hashmicro.com",
    'depends': [
        'l10n_sg_hr_payroll',
    ],
    'data': [
        'data/salary_rule.xml'
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
