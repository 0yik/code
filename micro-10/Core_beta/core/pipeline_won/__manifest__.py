# -*- coding: utf-8 -*-
{
    'name': 'Pipeline Won',
    'version': '1.0',
    'category': 'Pipeline',
    'sequence': 5,
    'summary': 'setup for pipeline process of CRM',
    'description': "This module includes all CRM pipeline process related setup",
    'website': 'http://www.axcensa.com/',
    'author': 'Axcensa',
    'depends': [
        'crm'
    ],
    'data': [
        'wizard/customer_wizard_view.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}