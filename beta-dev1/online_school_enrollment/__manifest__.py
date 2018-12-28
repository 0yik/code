# -*- coding: utf-8 -*-
{
    'name': 'Online School Enrollment',
    'version': '10.0.1.0.13',
    'author': "HashMicro / Inkal",
    'website':"http://www.hashmicro.com",
    'category': 'School Management',
    'license': "AGPL-3",
    'complexity': 'easy',
    'Summary': 'A Module For Online School Enrollment',
    'depends': ['website_payment', 'odoo_web_login','website', 'payment_paypal', 'school_fees'],
    'data': [
            'security/ir.model.access.csv',
            'views/assets.xml',
            'views/student_report_menu.xml',
            'views/student_report_template.xml',
            'views/email_template_view.xml',
            'views/thanks_template_view.xml',
            'views/admission_register_form_template_view.xml',
            'views/webclient_templates.xml',
            'views/website_footer_template.xml',
            ],
    'demo': [],
    # 'css': ['static/src/css/school.css'],
    'installable': True,
    'application': True
}
