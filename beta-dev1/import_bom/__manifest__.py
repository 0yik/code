# -*- coding: utf-8 -*-
{
    'name': 'Import BOM',
    'version': '1.0',
    'category': 'Manufacturing',
    'author': 'HashMicro/ MPTechnolabs - Bharat Chauhan',
    'website': "http://www.hashmicro.com",
    'summary': 'Import Bill of Materials',
    'depends': [
        'mrp',
    ],
    'data': [
        'wizard/import_bom_view.xml',
        'views/mrp_bom.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
