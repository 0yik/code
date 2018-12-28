
# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Student Vocational Education',
    'version': '10.0',
    'author': 'HashMicro / Ajay / Bhavik - TechnoSquare',
    'category': 'EMS',
    'sequence': 100,
    'summary': 'Vocational education to students',
    'description': """
Students Vocational Education
=============================
This application enables you to manage student vocational education..

    """,
    'website': 'www.hashmicro.com',
    'images': [
       
    ],
    'depends': ['atts_course','hr'],
    'data': [
        'views/vocational_education.xml',
        'security/ir.model.access.csv',
        
    ],
    'demo': [
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'qweb': [],
}
