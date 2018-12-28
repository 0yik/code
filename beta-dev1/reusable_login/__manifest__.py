# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Reusable Login',
    'version': '10.0',
    'author': 'HashMicro/Satya',
    'category': 'Setting',
    'sequence': 100,
    'summary': 'Login attempts by user',
    'description': """
Reusable Login
==============
This application enables you to manage user login attempts....

    """,
    'website': 'www.hashmicro.com',
    'images': [
       
    ],
    'depends': ['base','web'],
    'data': [
        'views/res_users.xml',
    ],
    'demo': [
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'qweb': [],
}
