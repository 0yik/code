# -*- coding: utf-8 -*-
{
    'name': "Modifier TEO Contract",

    'summary': """
        Added fields in HR/ Contract Form
    """,
    'description': """
    """,

    'author': "HashMicro / Satya",
    'website': "www.hashmicro.com",

    'category': 'Human Resources',
    'version': '10.0',

    'depends': ['hr_contract','l10n_sg_hr_payroll'],

    'data': [
        'views/hr_contract_view.xml',
    ],
    'installable': True,
}