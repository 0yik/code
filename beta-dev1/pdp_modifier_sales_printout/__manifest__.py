# -*- coding: utf-8 -*-
{
    'name': 'PDP Modifier Sales Printout',
    'version': '1.0',
    'category': 'sales',
    'sequence': 18,
    'description': "Modify sale order report.",
    'website': 'http://www.hashmicro.com/',
    'author': 'Hashmicro/ MPTechnolabs- Komal Kaila',
    'depends': ['sale'],
    'data': [
        'views/sale_order_report.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}