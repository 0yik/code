# -*- coding: utf-8 -*-
{
    'name': "payment_followup",

    'summary': """
        payment_followup""",

    'description': """
        payment_followup
    """,

    'author': "HashMicro / MPTechnolabs - Dhaval",
    'website': "https://www.hashmicro.com",

    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['account_followup', 'task_list_manager'],

    # always loaded
    'data': [
        'views/account_followup_views.xml',
    ],
    'installable': True,
    'auto_install': False
}