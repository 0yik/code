# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Helpdesk Extension',
    'version': '1.0',
    'category': 'Helpdesk',
    'sequence': 1,
    'author': 'HashMicro /Komal Kaila /Vu',
    'summary': 'Added new button Tickets on Customer ',
    'description': """
    """,
    'website': 'www.hashmicro.com',
    'images': [],
    'depends': [
        'base',
        'helpdesk',
        'mail',
    ],
    'data': [
        'views/res_partner_view.xml',
        'views/helpdesk_ticket_views.xml',
        'views/helpdesk_team_view.xml',
        'views/loop_email_view.xml',
    ],
    'demo': [
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'qweb': [],
}
