
# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Database Information',
    'version': '10.0',
    'author': 'HashMicro/Naresh',
    'category': 'Genreal DB Information',
    'sequence': 100,
    'summary': 'This module contains the information of installed modules',
    'description': """
Database Information
====================
This application creates a excel report and fetches the installed module information

    """,
    'website': 'www.hashmicro.com',
    'images': [
       
    ],
    'depends': ['base'],
    'data': [
        'view/db_info_view.xml',
        
    ],
    'demo': [
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'qweb': [],
}
