# -*- coding: utf-8 -*-
{
    'name': 'Collector Invoice',
    'version': '1.0',
    'category': 'Accounting',
    'author': 'HashMicro/ MPTechnolabs - Komal Kaila',
    'website': "http://www.hashmicro.com",
    'summary': 'Collector Invoice',
    'depends': [
        'account',
    ],
    'data': [
        'views/account_invoice_view.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'AGPL-3',
}
