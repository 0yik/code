# -*- coding: utf-8 -*-
{
    'name': 'RFQ Approval Request',
    'version': '1.0',
    'category': 'Purchase',
    'sequence': 17,
    'summary': 'setup for sending mail notification and mail to approver.',
    'description': "This module includes sending mail notification and mail for approver to approve quotation.",
    'website': 'http://www.hashmicro.com/',
    'author': 'Hashmicro/Kannan',
    'depends': ['purchase','hr'],
    'data': [
        'views/purchase_view.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}