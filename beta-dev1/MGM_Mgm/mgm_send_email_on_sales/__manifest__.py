# -*- coding: utf-8 -*-
{
    'name': 'MGM send email on sales',
    'version': '1.0',
    'category': 'sale',
    'summary': 'setup for sending mail notification and mail to approver.',
    'description': "Send Email manualy to recipient with clickable link for sales orders.",
    'website': 'http://www.hashmicro.com/',
    'author': 'Hashmicro/Mareeswaran',
    'depends': ['sale', 'mail', 'sale_discount_total'],
    'data': [
        'data/sale_mail_data.xml',
        'wizard/mail_compose_message_view.xml',
        'views/sale_view.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}