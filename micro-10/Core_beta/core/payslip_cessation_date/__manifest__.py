# -*- coding: utf-8 -*-
{
    'name': 'Payslip Cessation Date',
    'description': "This module is to create payslip based on Employee's  Cessation date",
    'version': '1.0',
    'category': 'Payroll',
    'author': 'HashMicro/ MPTechnolabs(Chankya)',
    'website': "http://www.hashmicro.com",
    'depends': [
        'hr_payroll',
        'l10n_sg_hr_payroll',
    ],
    'data': [
        'data/salary_rule.xml'
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}