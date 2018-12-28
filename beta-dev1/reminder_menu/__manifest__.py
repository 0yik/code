{
    'name': "Reminder Notification",
    'version': '0.1',
    'category': 'crm',
    'description': """
    """,
    'author': "HashMicro / Parikshit Vaghasiya",
    'website': "http://www.hashmicro.com",
    'depends': ['base','sale'],
    'data': [
        'views/reminder_notification_view.xml',        
    ],
    'qweb': [
        "static/src/xml/notification_reminder.xml",
    ],
}