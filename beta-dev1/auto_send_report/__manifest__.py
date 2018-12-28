# -*- coding: utf-8 -*-
{
    'name': "auto_send_report",

    'summary': """
        Allow auto sending report of pre created filters in the system""",

    'description': """
Flow:
1. User creates a favorite filter called Filter A, normally user can download to excel in the reporting tab
2. Add a menu where you can select the filters that was pre-created, and the recipients, and the frequency of the sending
3. Once saved, it will create a scheduler that renders an excel based on the filter and sends to the recipients on a periodical basis
    """,

    'author': "HashMicro / Vu",
    'website': "http://www.hashmicro.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'HashMicro',
    'version': '1.0',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'mail',
    ],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/config_views.xml',
        'data/data.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}