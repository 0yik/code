# -*- coding: utf-8 -*-
{
    'name': 'Accrual Unpaid Leave Payroll',
    'version': '1.0',
    'category': 'Human Resources',
    'sequence': 7,
    'summary': 'setup for HR Manager generated employee payslip on 25/6/2018. Employee apply unpaid leave=29/6/2018 (after the payslip generation), system will deduct the unpaid leave=29/6/2018 in July payslip.',
    'description': "This module includes setup for HR Manager generated employee payslip on 25/6/2018. Employee apply unpaid leave=29/6/2018 (after the payslip generation), system will deduct the unpaid leave=29/6/2018 in July payslip.",
    'website': 'http://www.hashmicro.com/',
    'author': 'Hashmicro/Kannan',
    'depends': [
        'l10n_sg_hr_payroll',
    ],
    'data': [
        'views/hr_payslip_view.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}