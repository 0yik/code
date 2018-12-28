# -*- coding: utf-8 -*-
{
    'name': "Manufacturing Disassemble",
    'description': "This module will helps to disassemble the products",
    'summary': 'Disassembling the products',
    'author': "HashMicro/Saravanakumar",
    'website': "www.hashmicro.com",
    'category': 'Product',
    'version': '1.0',
    'depends': ['base', 'stock'],
    'data': [
        'security/ir.model.access.csv',
        'data/disassemble_data.xml',
        'views/res_disassemble_views.xml',
        'views/res_assemble_views.xml',
    ],
    'application': True
}