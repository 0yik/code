# -*- coding: utf-8 -*-
{
    'name': 'Document Management Access Rights',
    'version': '1.0',
    'category': 'Document Management Access Rights',
    'sequence': 7,
    'summary': 'setup for document access rights based on groups',
    'description': "This module includes setup for document management access rights based on groups during user creation",
    'website': 'http://www.axcensa.com/',
    'author': 'Axcensa',
    'depends': [
        'access_rights_group','muk_dms'
    ],
    'data': [
        #'security/ir.model.access.csv',
        'views/muk_directory_view.xml',
        'views/muk_file_view.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
