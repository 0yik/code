# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Account Contact Modifier',
    'version': '1.0',
    'category': 'Account',
    'summary': 'Add button to link children to parent customer',
    'description': """
    """,
    'author': 'HashMicro / Quy',
    'website': 'www.hashmicro.com',
    'depends': [
        'base',
    ],
    'data': [
        'views/res_partner_view.xml'
        ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
