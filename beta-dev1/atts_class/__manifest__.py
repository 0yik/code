
# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'ATTS Class',
    'version': '10.0',
    'author': 'HashMicro / Ajay / Bhavik - TechnoSquare',
    'category': 'EMS',
    'sequence': 100,
    'summary': 'class information of students',
    'description': """
Students Class Information
==========================
This application enables you to manage students class information..

    """,
    'website': 'www.hashmicro.com',
    'images': [
       
    ],
    'depends': ['atts_course','hr','atts_student_fields','atts_english_math_level','web_widget_timepicker'],
    'data': [
        'wizard/class_placement_wizard.xml',
        'views/views.xml',
        'views/report_class_summary.xml',
        'views/report_class.xml',
        'wizard/report_class_summary_wizard.xml',
        'wizard/report_class_group_wizard.xml',
        'wizard/report_class_list_wizard.xml',
        'views/report_class_group.xml',
        'views/report_class_list.xml',
        'security/ir.model.access.csv',
        
    ],
    'demo': [
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'qweb': [],
}
