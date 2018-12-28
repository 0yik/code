# -*- coding: utf-8 -*-
{
    'name': 'Consignment Notes',
    'version': '1.0',
    'category': '',
    'sequence': 7,
    'summary': 'Consignment Agreement and auto update the status of the agreement ',
    'description': "Consignment Agreement and auto update the status of the agreement ",
    'website': '',
    'author': 'hashmicro/ Janbaz Aga',
    'depends': [
        'stock','account'
    ],
    'data': [
        'data/sequence.xml',
        'views/consignment_notes.xml',
        'views/consignment_invoice.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
