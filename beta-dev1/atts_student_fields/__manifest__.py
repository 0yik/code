# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'ATTS Student Information',
    'version': '1.0',
    "author": 'HashMicro / Ajay / Bhavik - TechnoSquare',
    'category': 'School Management',
    'sequence': 15,
    "website": "www.hashmicro.com",
    'summary': 'School Management Customization',
    'description': """
Manages Student information
==================================
    """,
    'depends': ['base','atts_course','atts_vocational_education'],
    'data': [
             'views/res_partner_view.xml',
             'views/student_view.xml',
             'data/country_data.xml',
             'report/report_student_detail.xml',
             'report/student_report.xml',
             'security/ir.model.access.csv',
             'wizard/monthly_enrolment.xml',
             'report/enrolment_by_gender_report.xml',
             'wizard/enrolment_by_gender_view.xml',
             'report/enrolment_by_student_nationality.xml',
             'report/health_datasheet_report.xml',
             'report/enrolment_by_religion.xml',
             'report/enrolment_by_race.xml',
             'report/monthly_withdrawl_report.xml',
             'data/student_data.xml',
             
    ],
    'demo': [
    ],
    'css': [],
    'installable': True,
    'auto_install': False,
    'application': True,
}
