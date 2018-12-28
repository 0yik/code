# -*- coding: utf-8 -*-
{
    'name': "Enterprise Accounting Report",
    'summary': "Enterprise Accounting Report",
    'description': "Accounting Reports",
    'author': "HashMicro / Saravanakumar",
    'website': "www.hashmicro.com",
    'category': 'account',
    'version': '1.0',
    'depends': [
        'account_accountant','l10n_sg', 'sale', 'purchase', 'stock', 'report'
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/init.yml',
        'data/account_financial_report_data.xml',
        'views/report_view.xml',
        'views/account_config_settings_views.xml',
        'views/account_journal_dashboard_view.xml',
        'views/account_report_view.xml',
        'views/partner_view.xml',
        'views/report_financial.xml',
        'views/report_followup.xml',
        'data/menu.sql',
    ],
    'qweb': [
        'static/src/xml/account_report_backend.xml',
    ],
    'installable': True,
    'auto_install': False,
}
