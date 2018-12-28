# -*- coding: utf-8 -*-
{
    'name': 'Student Portal',
    'version': '10.0.1.0.13',
    'author': "HashMicro / Inkal",
    'website':"http://www.hashmicro.com",
    'category': 'School Management',
    'license': "AGPL-3",
    'complexity': 'easy',
    'Summary': 'A Module For Student Portal',
    'depends': ['application_fees_per_course', 'school_assignment_ems'],
    'data': [
            # 'security/ir.model.access.csv',
            # 'security/student_security.xml',
            # 'views/invoice_view.xml',
            # 'views/payment_transaction_view.xml',
            'views/student_portal_invoice_template_view.xml',
            'views/student_portal_reminders_template_view.xml',
            'views/student_portal_profile_template_view.xml',
            'views/student_portal_classes_schedulers_template_view.xml',
            'views/student_portal_assignment_template_view.xml',
            'views/student_portal_exam_template_view.xml',
            'views/student_portal_exam_result_template_view.xml',
            'views/student_portal_attendance_template_view.xml',
            'views/student_portal_grades_template.xml',
            'views/template_view.xml',
            'views/student_portal_menu_view.xml',
            ],
    'demo': [],
    'css': ['static/src/css/portal.css'],
    'installable': True,
    'application': True
}
