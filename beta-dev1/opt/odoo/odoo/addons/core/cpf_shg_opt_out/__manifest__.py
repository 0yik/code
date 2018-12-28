# -*- coding: utf-8 -*-
{
    'name': 'Opt Out CPF SHG',
    'summary': """Employee can choose to opt out CPF – CDAC, MBMF, SINDA, ECF.""",
    'description': """Employee can choose to opt out CPF – CDAC, MBMF, SINDA, ECF.
        These salary rules would not applied on the employee payslip if they opt out.""",
    "author": u"HashMicro / Abulkasim Kazi",
    "website": u"www.hashmicro.com",
    "version": '1.0',
    'category': 'HR',
    'depends': ['l10n_sg_hr_payroll'],
    'license': 'LGPL-3',
    'data': [
        'views/hr_employee.xml',
    ],
    'demo': [],
    'images': [],
    'application': True,
    'installable': True,
    'auto_install': False,
}
