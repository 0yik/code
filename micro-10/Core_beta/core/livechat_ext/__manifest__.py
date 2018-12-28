# -*- coding: utf-8 -*-
{
    'name': 'Live Chat Ext',
    'version': '1.0',
    'category': 'chat',
    'sequence': 15,
    'summary': 'Website chat changes required for hashmicro',
    'description': "This module includes the start page in website to get the name and email of the visitor",
    'website': 'http://www.axcensa.com/',
    'author': 'Hashmicro/Axcensa',
    'depends': ['im_livechat', 'website_helpdesk_livechat'],
    'data': [
        'views/im_livechat_define.xml',
        'views/mail_channel_views.xml',
        'views/res_user_view.xml',
    ],
    'qweb': [
        'static/src/xml/chat_window_ext.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}