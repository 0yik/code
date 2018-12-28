# -*- coding: utf-8 -*-
{
    'name' : 'Catering',
    'version' : '1.0',
    'category': 'sales Management',
    'author': 'HashMicro / MP technolabs / Mital',
    'description': """Catering Management.
    """,
    'website': 'www.hashmicro.com',
    'depends' : ['base', 'mrp', 'stable_account_analytic_analysis'],
    'data': [
		'view/account_analytic_analysis_view.xml',
        'view/account_analytic_analysis_cron_job.xml',
    ],
    'demo': [
    ],
    'qweb': [
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
