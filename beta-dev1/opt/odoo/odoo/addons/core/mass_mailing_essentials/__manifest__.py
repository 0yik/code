# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Mass Mailing Essentials',
    'version': '1.0',
    "author": "HashMicro/ Naresh",
    'category': 'Sale',
    'sequence': 15,
    "website": "www.hashmicro.com",
    'summary': 'Mass Mailing Essentials',
    'description': """
          Added Modifications in mass mailng module
    """,
    'depends': ['mass_mailing'],
    'data': [
#              'views/mass_mailing_view.xml',
             'views/editor_field_html.xml',
    ],
    'demo': [
    ],
    'css': [],
    'installable': True,
    'auto_install': False,
    'application': True,
}
