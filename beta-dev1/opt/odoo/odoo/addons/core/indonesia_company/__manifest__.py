# -*- coding: utf-8 -*-
{
    'name': 'Indonesia Company',
    'version': '1.0',
    'category': 'Settings',
    'sequence': 5,
    'summary': 'setup for adding new fields into the Company setup for Indonesian Payroll Tax',
    'description': "This module includes adding new fields into the Company setup for Indonesian Payroll Tax",
    'website': 'http://www.hashmicro.com/',
    'author': 'Hashmicro/Kannan',
    'depends': ['province_wage_range'],
    'data': [
        'views/res_company.xml',
    ],
    'installable': True,
    'auto_install': True,
    'application': True,
}