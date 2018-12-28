# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Force Password Changing',
    'version': '10.0',
    'author': 'HashMicro/Satya',
    'category': 'Setting',
    'sequence': 100,
    'summary': 'Force Password Changing',
    'description': """
Force Password Changing
=======================
This application enables you to manage user password....

    """,
    'website': 'www.hashmicro.com',
    'images': [
       
    ],
    'depends': ['base','web','reusable_login'],
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
