# -*- coding: utf-8 -*-
{
    'name': 'Donation Management',
    'summary': 'Allow users to record donations from different donors',
    'description': 'Donation management : Allow users to record donations from different donors',
    'version': '1.0',
    'category': 'Uncategorized',
    'author': 'Hashmicro/Saravanakumar',
    'website': 'www.hashmicro.com',
    'depends': ['sale'],
    'data': [
        'security/ir.model.access.csv',
        'data/account.xml',
        'views/donation_view.xml',
        'views/partner_view.xml',
    ],
    'application': True,
}
