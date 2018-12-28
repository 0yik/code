# -*- coding: utf-8 -*-

{
    'name': 'Mass Mailing Campaigns',
    'summary': 'Design, send and track emails',
    'description': """
    Mass Mailing Extension
    """,
    'version': '1.1',
    'author': 'HashMicro / Janeesh',
    'website': 'www.hashmicro.com',
    'category': 'Marketing',
    'depends': [
        'mass_mailing',
    ],
    'data': [
        'wizard/create_mass_mailing_view.xml',
        'wizard/mass_mailing_preview_view.xml',
        'views/mass_mailing_views.xml',
        'views/mass_mailing_report_views.xml',
        'views/snippet.xml',
    ],
    'demo': [
    ],
    'application': True,
}
