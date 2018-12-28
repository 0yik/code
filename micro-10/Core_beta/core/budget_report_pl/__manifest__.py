# -*- coding: utf-8 -*-
{
    'name': 'Budget Report P&L',
    'category': 'Account',
    'summary': 'Budget Management Extension',
    'description': 'Budget Profit & Loss Reporting',
    'sequence': 10,
    'author': 'HashMicro/Saravanakumar',
    'website': 'www.hashmicro.com',
    'version': '1.0',
    'depends': ['account', 'account_accountant'],
    'data': [
        'security/ir.model.access.csv',
        'views/report_pl_view.xml',
        'report/budget_report.xml',
        'report/budget_report_templates.xml',
    ],
    'installable': True,
    'application': True,
}
