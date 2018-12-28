# -*- coding: utf-8 -*-
{
    'name' : 'Laborindo Report Sales Order',
    'version' : '1.0',
    'category': 'sale',
    'author': 'HashMicro / MP technolabs / Bipin Prajapati',
    'description': """Laborindo Report Sales Order
    """,
    'website': 'www.hashmicro.com',
    'depends' : ['sale','sales_team'],
    'data': [
        'report/sale_report.xml',
        'report/sale_report_templates.xml',
        'report/sale_report_labo.xml',
        'wizard/sale_report_view.xml',
    ],
    'demo': [

    ],
    'qweb': [

    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
