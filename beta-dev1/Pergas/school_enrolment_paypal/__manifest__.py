# -*- coding: utf-8 -*-
{
    'name': 'School Enrolment Paypal',
    'version': '10.0.1.0.13',
    'author': "HashMicro / Inkal",
    'website':"http://www.hashmicro.com",
    'images': ['static/description/school.png'],
    'category': 'School Enrolment Paypal',
    'license': "AGPL-3",
    'complexity': 'easy',
    'Summary': 'A Module School Enrolment Paypal',
    'depends': ['online_school_enrollment'],
    'data': [
            'security/ir.model.access.csv',
            'views/payment_template_view.xml',
            ],
    'demo': [],
    'installable': True,
    'application': True
}
