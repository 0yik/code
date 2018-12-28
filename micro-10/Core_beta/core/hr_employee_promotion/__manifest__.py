# -*- coding: utf-8 -*-
{
    'name': "HR Employee Promotion",
    'summary': """HR Employee Promotion.""",
    'author': "HashMicro/ MP Technolabs/ Vatsal",
    'website': "https://www.hashmicro.com/",
    'category': 'HR',
    'version': '1.2',
    'depends': ['base','hr','gamification','hr_contract','recruitment_checklist','sg_hr_employee'],

    'data': [
        'security/ir.model.access.csv',
        'views/job_posiiton_view.xml',
        'views/promotion_request_view.xml',
        'data/hr_employee_promotion_data.xml',
    ],

    'installable': True,
    'application': True,
    'auto_install': False,
}
