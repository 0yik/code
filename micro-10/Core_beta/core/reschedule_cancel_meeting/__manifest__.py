{
    'name': 'Reschedule Cancel Meeting',
    'version': '1.0',
    'depends': ['calendar'],
    'data': [
        'wizard/reschedule_wizard.xml',
        'wizard/cancel_wizard.xml',
        'views/calendar_reasons.xml',
        'views/calendar_calendar.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'auto_install': False,
}
