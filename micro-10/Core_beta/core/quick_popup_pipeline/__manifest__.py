{
    'name': 'Quick Popup Pipeline',
    'description': 'This module will add fields in Create Opportunity Popup Wizard.',
    'category': 'CRM',
    'version': '1.0',
    'author': 'HashMicro / MP Technolabs',
    'website': 'www.hashmicro.com',
    'depends': ['crm', 'account', 'crm_phonecall'],
    'data': [
        'views/calendar_view.xml',
        'views/crm_lead.xml',
        'views/crm_activity_log_view.xml',
    ],
    'application': True,
    'installable': True,
}