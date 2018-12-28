# -*- coding: utf-8 -*-
{
    'name': 'Indonesia HR Employee',
    'version': '1.0',
    'category': 'Human Resources',
    'sequence': 7,
    'summary': 'setup for adding new fields into the Employee Form for Indonesian Payroll Tax',
    'description': "This module includes adding new fields into the Employee Form for Indonesian Payroll Tax",
    'website': 'http://www.hashmicro.com/',
    'author': 'Hashmicro/Kannan',
    'depends': ['indonesia_company','indonesia_income_tax','l10n_sg_hr_payroll'],
    'data': [
        'views/hr_view.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}