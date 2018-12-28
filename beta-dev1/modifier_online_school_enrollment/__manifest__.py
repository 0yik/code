# -*- coding: utf-8 -*-
{
    'name': 'Modifier Online School Enrollment',
    'version': '10.0.1.0.13',
    'author': "HashMicro / Inkal",
    'website':"http://www.hashmicro.com",
    'category': 'School Management',
    'license': "AGPL-3",
    'complexity': 'easy',
    'Summary': 'A Module For Online School Enrollment',
    'depends': ['online_school_enrollment', 'school_enrolment_paypal'],
    'data': [
            'security/ir.model.access.csv',
            'views/assets_view.xml',
            'views/student_report_menu.xml',
            'views/student_report_template.xml',
            'views/student_payslip_report_template_view.xml',
            'views/education_background_view.xml',
            'views/highest_qualification_view.xml',
            'views/general_survey_view.xml',
            'views/admission_register_view.xml',
            'views/student_payslip_view.xml',
            'views/admission_register_form_template_view.xml',
            ],
    'demo': [],
    'installable': True,
    'application': True
}
