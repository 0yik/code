
# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Student CCA Session',
    'version': '10.0',
    'author': 'HashMicro/Satya',
    'category': 'EMS',
    'sequence': 100,
    'summary': 'Student CCA session',
    'description': """
Students CCA session
====================
This application enables you to manage students CCA session..

    """,
    'website': 'www.hashmicro.com',
    'images': [
       
    ],
    'depends': ['school','hr','gos_class'],
    'data': [
        'views/student_cca.xml',
        'security/ir.model.access.csv',
        
    ],
    'demo': [
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'qweb': [],
}
