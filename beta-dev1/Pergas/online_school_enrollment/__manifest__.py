# -*- coding: utf-8 -*-
{
    'name': 'Online School Enrollment',
    'version': '10.0.1.0.13',
    'author': "HashMicro / Inkal",
    'website':"http://www.hashmicro.com",
    # 'images': ['static/description/school.png'],
    'category': 'School Management',
    'license': "AGPL-3",
    'complexity': 'easy',
    'Summary': 'A Module For Online School Enrollment',
    'depends': ['odoo_web_login','website', 'payment_paypal', 'school_fees'],
    'data': [
            'security/ir.model.access.csv',
            'views/assets.xml',
            'views/education_background_view.xml',
            'views/admission_register_view.xml',
            'views/highest_qualification_view.xml',
            'views/general_survey_view.xml',
            'views/payment_template_view.xml',
            'views/thanks_template_view.xml',
            'views/admission_register_form_template_view.xml',
            'views/webclient_templates.xml',
            ],
    'demo': [],
    'installable': True,
    'application': True
}
