# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'InterFace Branding',
    'version': '1.1',
    'category': 'Web',
    'summary': 'User interface',
    'description': """
    """,
    'author':'Hashmicro / Parikshit Vaghasiya',
    'depends': ['base','web','web_responsive'],
    'qweb': ['static/src/xml/*.xml'],
    'data': [
        'security/ir.model.access.csv',
        'views/hm_system_view.xml',
    ],
    'installable': True,
    'auto_install': True,
}
