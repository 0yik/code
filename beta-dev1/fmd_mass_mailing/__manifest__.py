# -*- coding: utf-8 -*-
{
    'name': "FMD Mass Mailing Extended",
    'summary': """
        Extend Mass Mailing and Mass Mailing Contact View.
    """,
    'description': """
        
    """,
    'author': "Hashmicro / MpTechnolabs - Bhavin Jethva",
    'website': "www.hashmicro.com",
    'category': 'base',
    'version': '1.0',
    'depends': ['fmd_customer'],
    'data': [
        'views/mass_mailing_contact_view.xml',
    ],
    # only loaded in demonstration mode
    'installable': True,
}
