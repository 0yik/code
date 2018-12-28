# -*- coding: utf-8 -*-
{
    'name': "Modifier TEO HR",

    'summary': """
        Added fields in HR/ Expense Form
    """,
    'description': """
    """,

    'author': "HashMicro / Ajay Patel, MpTechnolabs - Bhavin Jethva",
    'website': "www.hashmicro.com",

    'category': 'Human Resources',
    'version': '1.0',

    'depends': ['hr', 'hr_expense', 'modifier_teo_leave_management',
                'hr_attendance', 'sg_hr_report', 'hm_hr_sg_standardization'],

    'data': [
        'security/ir.model.access.csv',
        'security/hr_expense_security.xml',
        'data/data.xml',
        'views/hr_expense_view.xml',
        'views/hr_employee_view.xml',
    ],
    'installable': True,
}
