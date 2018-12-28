# -*- coding: utf-8 -*-
{
    'name' : 'Aikchin Modifier Fields (HR)',
    'version' : '1.0',
    'category': 'HR',
    'author': 'HashMicro / MP technolabs / Mital',
    'description': """Modify the fields.
    """,
    'website': 'www.hashmicro.com',
    'depends' : ['hr', 'l10n_sg_hr_payroll', 'sg_hr_employee', 'sale_timesheet', 'hr_contract', 'hr_payroll', 'hr_holidays', 'employee_appraisal'],
    'data': [
		'view/hr_employee_view.xml', 
    ],
    'demo': [
    ],
    'qweb': [
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
