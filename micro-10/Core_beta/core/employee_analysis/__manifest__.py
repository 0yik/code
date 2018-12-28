# -*- coding: utf-8 -*-
{
    'name': 'Employee Analysis',
    'summary': """Employee Analysis""",
    'description': """Allow employee analysis with the fields: Employee, Department,
            Job Title, Branch, Manager., Date (day, week, month, year) Measures are: Count,
            Active Contract Salary. Which is a pivot of Active employees.""",
    "sequence": 1,
    "author": u"HashMicro / Abulkasim Kazi",
    "website": u"www.hashmicro.com",
    "version": '1.0',
    'category': 'HR',
    'depends': ['hr', 'sg_hr_employee'],
    'license': 'LGPL-3',
    'data': [
        'security/ir.model.access.csv',
        'views/menu_payslip_report.xml',
    ],
    'demo': [],
    'images': [],
    'application': True,
    'installable': True,
    'auto_install': False,
}
