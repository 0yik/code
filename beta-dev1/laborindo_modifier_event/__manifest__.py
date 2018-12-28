# -*- coding: utf-8 -*-
{
    'name' : 'Laborindo Modifier Event',
    'version' : '1.0',
    'category': '',
    'author': 'HashMicro / Abulkasim Kazi',
    'description': """Add customize field to event form and link questionnaire to event.""",
    'website': 'www.hashmicro.com',
    'depends' : ['event_sale','laborindo_customer_questionnaire'],
    'data': [
        'views/modifier_event_view.xml',
    ],
    'demo': [],
    'qweb': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}
