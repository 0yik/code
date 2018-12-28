# -*- coding: utf-8 -*-
{
    'name': "mail_auto_reply",

    'description': """
        Add "Email Template" field in incoming mail servers
        The email template is a dropdown of all email templates
        When an email is received to this incoming mail server, that email template is sent
    """,

    'author': "HashMicro / Hoang",
    'website': "http://www.hashmicro.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '1.0',

    # any module necessary for this one to work correctly
    'depends': ['base', 'mail', 'fetchmail'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}