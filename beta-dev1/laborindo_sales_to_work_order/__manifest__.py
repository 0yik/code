# -*- coding: utf-8 -*-
{
    'name' : 'Laborindo Sales To Work Order',
    'version' : '1.0',
    'category': 'sale',
    'author': 'HashMicro / MP technolabs / Bipin Prajapati',
    'description': """Laborindo Sales To Work Order
    """,
    'website': 'www.hashmicro.com',
    'depends' : ['sale','task_list_manager'],
    'data': [
        'data/sequence_data.xml',
        'data/mail_data.xml',
        'views/sale_view.xml',
        'views/work_order_view.xml',

    ],
    'demo': [

    ],
    'qweb': [

    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
