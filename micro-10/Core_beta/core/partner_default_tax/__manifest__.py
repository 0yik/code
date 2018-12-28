# -*- coding: utf-8 -*-
{
    'name': 'Partner Default Tax',
    'version': '1.0',
    'category': 'Account',
    'author': 'Hashmicro / Saravanakumar',
    'summary': 'Partner based default taxes in sales / purchase / invoice',
    'description': '''This module will add default taxes in company and customer.
    Based on tax configuration in company & partner taxes will update in Sales order, Purchase order, and invoices''',
    'website': 'https://www.hashmicro.com',
    'depends': ['sale', 'purchase'],
    'data': [
        'views/company_view.xml',
        'views/partner_view.xml',
    ],
    'installable': True,
    'application': True,
}
