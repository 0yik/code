# -*- coding: utf-8 -*-
{
    'name': 'Hashmicro Bom POS Import',
    'description': 'This module intends to have functionality to reduce bill of materials in inventory when importing POS process is done',
    'version': '1.0',
    'category': 'Point Of Sale',
    'author': 'HashMicro/ MPTechnolabs(Chankya)',
    'website': "http://www.hashmicro.com",
    'depends': [
        'import_pos','branch','mrp'
    ],
    'data': [
        'views/mrp_bom_view.xml',
#         'wizard/pos_import_view.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
