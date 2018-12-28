# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Manufacturing efficiency',
    'version': '1.0',
    "author": "HashMicro/ Naresh",
    'category': 'Base',
    'sequence': 15,
    "website": "www.hashmicro.com",
    'summary': 'Manufacturing efficiency',
    'description': """
Set up manufacturing efficiency in BoM
==================================
    """,
    'depends': ['base','bom_pos_modifier'],
    'data': [
             'view/manufacturing_efficiency_view.xml'
    ],
    'demo': [
    ],
    'css': [],
    'installable': True,
    'auto_install': False,
    'application': True,
}
