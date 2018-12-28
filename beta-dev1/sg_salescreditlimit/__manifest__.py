# -*- coding: utf-8 -*-
{
    'name': 'Sg Salescreditlimit',
    'version': '1.0',
    'category': 'Sale',
    'sequence': 15,
    'summary': 'setup for customer credit limit',
    'description': "This module includes customer credit limit setup for sale order process",
    'website': 'http://www.axcensa.com/',
    'author': 'Axcensa',
    'depends': [
        'sale'
    ],
    'data': [
        'security/sale_security.xml',
        'views/sale_view.xml',
        'views/res_partner_view.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}