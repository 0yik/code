# -*- coding: utf-8 -*-
{
    'name': "Email Management",

    'description': """
        -1. Add a popup when clicking “Send Message” in any records.
        -2. Add HTML editor 
        -3. Implement Mail Inbox
    """,

    'author': "HashMicro / Vu",
    'website': "http://www.hashmicro.com",

    'category': 'Discuss',
    'version': '1.0',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'mail',
        'fetchmail',
        'web',
    ],

    # always loaded
    'data': [
        'data/cron.xml',
        'data/data.xml',
        'security/record_rules.xml',
        'security/ir.model.access.csv',
        'views/mail_mail_views.xml',
        'views/fetchmail_server_views.xml',
        'views/mail_server_source_views.xml',
        'views/ir_mail_server.xml',
        # 'views/ir_mail_server_source_view.xml',
        'views/template.xml',
        'views/res_users.xml',
    ],
    'qweb': ['static/src/xml/mail_inbox.xml'],
    # only loaded in demonstration mode
    'demo': [
    ],
    'images': ['static/description/icon.png'],
    'installable': True,
    'application': True,
}
