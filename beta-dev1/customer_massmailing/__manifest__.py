# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': "Customer Massmailing",
    'version': "1.0",
    'summary': "Customer Massmailing",
    'author': "HashMicro/MP Technolabs/Purvi",
    'website': "http://www.hashmicro.com",
    'category': "Marketing",
    'depends': ['crm','mass_mailing'],
    'data': [
        'views/res_partner_views.xml',
    ],
    'demo': [],
    'application': True,
}