# -*- coding: utf-8 -*-
{
    'name': 'Inventory Extended',
    'version': '1.0',
    'category': 'stock',
    'author': 'HashMicro/ MPTechnolabs - Komal Kaila',
    'description' : '''Add Graph View to the Inventory
    ''',
    'website': "http://www.hashmicro.com",
    'summary': 'Add Graph View to the Inventory',
    'depends': [
        'stock',
    ],
    'data': [
        'views/inventory_view.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'AGPL-3',
}
