# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': ' Custom Record Filter For Enquiry Stage',
    'version': '1.2',
    'category': 'Sale',
    'summary': 'Custom Record Filter For Enquiry Stage',
    'description': """
    This module generates record filter for Enquiry Stage
    """,
    'author': 'HashMicro / GeminateCS',
    'website': 'www.hashmicro.com', 
    'depends': [
        'crm',
        'sale',
    ],
    'data': [
        'views/crm_lead_view.xml',
        'views/partner_view.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}