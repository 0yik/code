# -*- coding: utf-8 -*-
# Copyright 2016 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': "Mail Optional Follower Notification",

    'summary': """
        Choose if you want to automatically notify followers
        on mail.compose.message""",
    'author': 'HashMicro / Quy',
    'website': "https://www.hashmicro.com/",
    'category': 'mail',
    'version': '10.0.1.0.1',
    'depends': [
        'mail',
    ],
    'data': [
        'wizard/mail_compose_message_view.xml',
    ],
}
