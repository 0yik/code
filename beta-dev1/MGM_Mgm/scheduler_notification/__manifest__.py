{
    'name': 'Scheduler Notification',
    'version': '1.0',
    'category': 'Account',
    'summary': "Scheduler Notification",
    'author': "HashMicro/MP Technolabs/ vatsal",
    'website': "http://www.hashmicro.com",

    'description': """

Scheduler Notification
=======================
Module to manage Scheduler Notification
""",
    'depends': ['base','web','account','hr','task_list_manager'],
    'data': [
        'security/ir.model.access.csv',
        'views/scheduler_notification_template.xml',
        'views/schedule_notification_setup_view.xml',
        'views/schedule_reminder_popup_view.xml',
    ],
    'demo': [
    ],
    'qweb': [
        'static/src/xml/chatter.xml',
        'static/src/xml/scheduler.xml',
    ],
    'images': [],
    'application': True,
    'installable': True,
    'auto_install': False,
}
