# -*- coding: utf-8 -*-
{
    'name': 'Import POS',
    'version': '1.0',
    'category': 'Point Of Sale',
    'author': 'HashMicro/ MPTechnolabs - Komal Kaila',
    'website': "http://www.hashmicro.com",
    'summary': 'Import point of sale data',
    'depends': [
        'point_of_sale',
    ],
    'data': [
        'wizard/pos_import_view.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
