# -*- coding: utf-8 -*-
{
    'name': 'DZH Support Report',
    'version': '1.0',
    'website': 'https://www.hashmicro.com',
    'category': 'CRM',
    'author':'Hashmicro / Parikshit Vaghasiya',
    'summary': 'Account Advisory Report Sending to Support Users.',
    'description': """
Account Advisory Report Sending to Support Users..
======================================
""",
    'depends': ['base', 'mail', 'report','crm'],
    'data': [
        'report/report_account_advisory_view.xml',
        'data/mail_template_data.xml',
        'views/dzh_support_views.xml',

    ],
    'installable': True,
    'auto_install': False,
}
