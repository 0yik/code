# -*- coding: utf-8 -*-
{
    'name': 'Forecast Report',
    'description': 'Create Forecast Report',
    'author': 'HashMicro / Duy / Saravanakumar',
    'website': 'http://www.hashmicro.com',
    'category': 'Accounting',
    'version': '1.0',
    'depends': ['base','sale','sales_team','account','enterprise_accounting_report'],
    'data': [
        'data/cashflow_statement.sql',
        'views/menu_forecast_report.xml',
    ],
    'installable': True,
    'application': True,
}