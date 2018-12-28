
# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'ATTS English Math Level',
    'version': '10.0',
    'author': 'HashMicro / Ajay / Bhavik - TechnoSquare',
    'category': 'EMS',
    'sequence': 100,
    'summary': 'English and math level information of student',
    'description': """
Students English and Math Level Information
===========================================
This application enables you to manage students english and math level information..

    """,
    'website': 'www.hashmicro.com',
    'images': [
       
    ],
    'depends': ['atts_course','hr','atts_student_fields'],
    'data': [
        'views/gos_level.xml',
        'security/ir.model.access.csv',
        
    ],
    'demo': [
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'qweb': [],
}
