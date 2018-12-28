# -*- coding: utf-8 -*-
{
    'name': "heldpesk_email_routing",

    'description': """
        Domain Routing for Helpdesk
    """,

    'author': "HashMicro / Vu",
    'website': "http://www.hashmicro.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '1.0',

    # any module necessary for this one to work correctly
    'depends': ['base', 'helpdesk', 'fetchmail'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/fetch_mail_server_views.xml',
        'views/helpdesk_email_routing_view.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}