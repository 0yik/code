# -*- coding: utf-8 -*-
{
    'name': 'employee loan extended',
    'version': '1.0',
    'category': 'HR',
    'author': 'HashMicro/ MPTechnolabs - Parikshit Vaghasiya',
    'website': "http://www.hashmicro.com",
    'summary': 'This module intends to have a functionality to manage loan from third party, ex: bank.',
    'depends': [
        'hr_employee_loan', 
    ],
    'data': [
        'views/employee_loan.xml',
        
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
