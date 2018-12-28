# -*- coding: utf-8 -*-
{
    'name': 'Adjustment Per GRN',
    'version': '1.0',
    'summary': 'Allows the user to adjust the quantity received from the GRN',
    'description': 'Allows the user to adjust the quantity received from the GRN',
    'category': 'Warehouse',
    'author': 'Hashmicro / Saravanakumar',
    'website': 'https://www.hashmicro.com',
    'depends': ['stock'],
    'data': [
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'views/stock_view.xml',
    ],
    'installable': True,
    'application': True,
}
