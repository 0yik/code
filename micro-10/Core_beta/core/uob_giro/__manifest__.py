# -*- coding: utf-8 -*-
{
    'name': 'UOB Bank Giro - Bulk Payment Services',
    'version': '1.0',
    'description': """
Singapore UOB bank giro file:
==============================================

Singapore UOB bank giro file generation :

* Generation of UOB bank giro file for vendor bills and payslip payment.

""",
    'author': 'Hashmicro/ Goutham',
    'category': 'Localization/Account Reports',
    'website': 'https://www.hashmicro.com/',
    'depends': ['account', 'hr_payroll'],
    'data': [
        'views/bank_view.xml',
        'wizard/giro_wizard.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
