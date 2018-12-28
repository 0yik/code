# -*- coding: utf-8 -*-
{
    'name': 'Multi Level Analytical',
    'version': '1.0',
    'summary': 'Enterprise accounting report with multi level analytical account',
    'description': 'Enterprise accounting report with multi level analytical account',
    'category': 'Accounting & Finance',
    'author': 'Hashmicro / Saravanakumar',
    'website': 'https://www.hashmicro.com',
    'depends': ['enterprise_accounting_report'],
    'data': [
        'views/define.xml',
        'views/analytic_level_view.xml',
    ],
    'qweb': [
        'static/src/xml/account_report_backend.xml',
    ],
    'installable': True,
    'application': True,
}
