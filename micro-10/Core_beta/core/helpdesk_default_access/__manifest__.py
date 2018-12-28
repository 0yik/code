# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Helpdesk Access Rights',
    'version': '1.1',
    'category': 'Helpdesk',
    'sequence': 1,
    'author': 'HashMicro /Komal Kaila',
    'summary': 'Modified Access Rights',
    'description': """
    """,
    'website': 'www.hashmicro.com',
    'images': [],
    'depends': [
        'base','helpdesk',
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/helpdesk_rule.xml',
        'views/helpdesk_ticket_view.xml',
    ],
    'demo': [
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'qweb': [],
}
