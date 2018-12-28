# -*- coding: utf-8 -*-
{
    'name': "mgm_modifier_recurring",

    'description': """
        Make auto notification
    """,

    'author': "HashMicro/Duy",
    'website': "http://www.hashmicro.com",
    'category': 'Uncategorized',
    'version': '1.0',

    # any module necessary for this one to work correctly
    'depends': ['base','account_accountant','account_asset'],

    # always loaded
    'data': [
        'data/cron.xml',
        'views/asset_notification.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}