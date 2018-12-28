# -*- coding: utf-8 -*-
{
    'name': 'Leave Encashment',
    'version': '1.0',
    'category': 'Leave Management',
    'sequence': 17,
    'summary': 'setup for user can define the leave type (e.g. Annual Leave) applicable for leave encashment based on unconsumed/balance leave days.',
    'description': "This module includes user can define the leave type (e.g. Annual Leave) applicable for leave encashment based on unconsumed/balance leave days.",
    'website': 'http://www.hashmicro.com/',
    'author': 'Hashmicro/Kannan',
    'depends': [
        'hr_leave_balance', 'l10n_sg_hr_payroll', 'sg_leave_constraints', 'past_dated_leave_allowed', 'sg_cpf_extended', 'termination_payslip'
    ],
    'data': [
        'data/salary_rule.xml',
        'views/hr_holidays_view.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}