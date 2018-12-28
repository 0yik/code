# -*- coding: utf-8 -*-
{
    'name': 'KTP Customer',
    'version': '1.0',
    'category': 'Sales',
    'sequence': 1,
    'summary': 'setup for customer master form',
    'description': "This module includes setup for customer master form kota, kelurahan, Provinsi and kecamatan.",
    'website': 'http://www.hashmicro.com/',
    'author': 'Hashmicro/ MP Technolabs - Purvi',
    'depends': [
        'vit_efaktur',
    ],
    'data': [
        'views/partner_view.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}