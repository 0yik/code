# -*- coding: utf-8 -*-
{
    'name': 'Pipeline Email',
    'version': '1.0',
    'category': 'Email',
    'sequence': 5,
    'summary': 'setup for email process of CRM',
    'description': "This module includes all CRM email process related setup",
    'website': 'http://www.axcensa.com/',
    'author': 'Axcensa',
    'depends': [
        'crm','email_management'
    ],
    'data': [
        'views/crm_lead_views.xml',
        'wizard/crm_activity_log_views.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}